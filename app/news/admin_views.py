from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import os
import glob
import json
import threading
import time
import csv
import datetime
from pathlib import Path
import pandas as pd

from .scraper import scrape_all_news, save_to_csv

# Global variables for batch tracking
active_batches = {}
batch_results = {}

def admin_required(user):
    """Check if user is admin/superuser"""
    return user.is_superuser

def get_data_directory():
    """Get the data directory path (Railway persistent storage)"""
    if os.path.exists("/app/data"):
        return "/app/data"
    else:
        # Local development fallback
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

def get_batch_files():
    """Get all news scraping batch files"""
    data_dir = get_data_directory()
    pattern = os.path.join(data_dir, "news_scrape_*.csv")
    files = glob.glob(pattern)
    
    batch_info = []
    for file_path in sorted(files, reverse=True):  # Newest first
        try:
            file_name = os.path.basename(file_path)
            # Extract timestamp from filename: news_scrape_YYYYMMDD_HHMMSS.csv
            timestamp_str = file_name.replace('news_scrape_', '').replace('.csv', '')
            
            # Get file stats
            stat = os.stat(file_path)
            file_size = stat.st_size
            created_time = datetime.datetime.fromtimestamp(stat.st_mtime)
            
            # Count rows in CSV
            try:
                with open(file_path, 'r') as f:
                    row_count = sum(1 for line in f) - 1  # Subtract header
            except:
                row_count = 0
            
            batch_info.append({
                'batch_id': timestamp_str,
                'file_name': file_name,
                'file_path': file_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / 1024 / 1024, 2),
                'created_time': created_time,
                'article_count': row_count,
                'status': 'completed'
            })
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    
    return batch_info

@login_required
@user_passes_test(admin_required)
def admin_scraper_home(request):
    """Main admin scraper interface"""
    context = {
        'active_batches': active_batches,
        'recent_batches': get_batch_files()[:5]  # Show 5 most recent
    }
    return render(request, 'admin_scraper/home.html', context)

@login_required
@user_passes_test(admin_required)
def list_batches(request):
    """List all scraping batches"""
    batches = get_batch_files()
    
    # Add active batch status
    for batch in batches:
        if batch['batch_id'] in active_batches:
            batch['status'] = active_batches[batch['batch_id']].get('status', 'running')
    
    context = {
        'batches': batches,
        'total_batches': len(batches)
    }
    return render(request, 'admin_scraper/batches.html', context)

@login_required
@user_passes_test(admin_required)
@require_POST
def start_scraping_batch(request):
    """Start a new scraping batch"""
    try:
        # Generate batch ID
        batch_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize batch status
        active_batches[batch_id] = {
            'status': 'starting',
            'start_time': datetime.datetime.now().isoformat(),
            'current_stage': 'Initializing scraper...',
            'articles_scraped': 0,
            'sources_completed': 0,
            'total_sources': 12
        }
        
        # Start scraping in background thread
        thread = threading.Thread(target=run_scraping_batch, args=(batch_id,))
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'success': True,
            'batch_id': batch_id,
            'message': 'Scraping batch started successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def run_scraping_batch(batch_id):
    """Background function to run the scraping batch"""
    try:
        # Update status
        active_batches[batch_id]['status'] = 'scraping'
        active_batches[batch_id]['current_stage'] = 'Starting news aggregation...'
        
        # Custom progress callback
        def progress_callback(stage, articles_count=0, sources_completed=0):
            if batch_id in active_batches:
                active_batches[batch_id].update({
                    'current_stage': stage,
                    'articles_scraped': articles_count,
                    'sources_completed': sources_completed
                })
        
        # Run the scraper with progress tracking
        progress_callback("Initializing scraper...")
        time.sleep(1)  # Small delay for UI
        
        # Import and modify scraper to use callback
        scraped_data = scrape_all_news_with_progress(batch_id, progress_callback)
        
        if scraped_data:
            # Save to CSV with batch ID
            progress_callback("Saving data to CSV...", len(scraped_data), 12)
            
            # Use custom filename with batch ID
            data_dir = get_data_directory()
            os.makedirs(data_dir, exist_ok=True)
            
            filename = f"news_scrape_{batch_id}.csv"
            filepath = os.path.join(data_dir, filename)
            
            df = pd.DataFrame(scraped_data)
            df.to_csv(filepath, index=False)
            
            # Update final status
            active_batches[batch_id].update({
                'status': 'completed',
                'current_stage': 'Completed successfully!',
                'end_time': datetime.datetime.now().isoformat(),
                'articles_scraped': len(scraped_data),
                'file_path': filepath
            })
            
            # Store results
            batch_results[batch_id] = {
                'csv_file': filepath,
                'article_count': len(scraped_data)
            }
        else:
            active_batches[batch_id].update({
                'status': 'failed',
                'current_stage': 'No articles were scraped',
                'end_time': datetime.datetime.now().isoformat()
            })
            
    except Exception as e:
        active_batches[batch_id].update({
            'status': 'failed',
            'current_stage': f'Error: {str(e)}',
            'end_time': datetime.datetime.now().isoformat()
        })

def scrape_all_news_with_progress(batch_id, progress_callback):
    """Modified version of scrape_all_news with progress tracking"""
    from .scraper import scrape_tech_techcrunch, scrape_tech_theverge
    from .scraper import scrape_economy_indianexpress, scrape_economy_economictimes
    from .scraper import scrape_sports_indianexpress, scrape_sports_hindustantimes
    from .scraper import scrape_politics_economictimes, scrape_politics_nytimes
    from .scraper import scrape_lifestyle_indianexpress, scrape_lifestyle_foxnews
    from .scraper import scrape_entertainment_indianexpress, scrape_entertainment_variety
    
    scraped_data = []
    scrapers = [
        ("TechCrunch", "Technology", scrape_tech_techcrunch),
        ("The Verge", "Technology", scrape_tech_theverge),
        ("Indian Express", "Economy", scrape_economy_indianexpress),
        ("Economic Times", "Economy", scrape_economy_economictimes),
        ("Indian Express", "Sports", scrape_sports_indianexpress),
        ("Hindustan Times", "Sports", scrape_sports_hindustantimes),
        ("Economic Times", "Politics", scrape_politics_economictimes),
        ("NY Times", "Politics", scrape_politics_nytimes),
        ("Indian Express", "Lifestyle", scrape_lifestyle_indianexpress),
        ("Fox News", "Lifestyle", scrape_lifestyle_foxnews),
        ("Indian Express", "Entertainment", scrape_entertainment_indianexpress),
        ("Variety", "Entertainment", scrape_entertainment_variety),
    ]
    
    for i, (source_name, category, scraper_func) in enumerate(scrapers):
        try:
            progress_callback(f"Scraping {source_name}...", len(scraped_data), i)
            
            data = scraper_func()
            scraped_data.extend(data)
            
            progress_callback(f"Completed {source_name} ({len(data)} articles)", len(scraped_data), i + 1)
            time.sleep(0.5)  # Small delay for UI updates
            
        except Exception as e:
            progress_callback(f"Error scraping {source_name}: {str(e)}", len(scraped_data), i + 1)
            continue
    
    return scraped_data

@login_required
@user_passes_test(admin_required)
def batch_status(request, batch_id):
    """Get status of a scraping batch"""
    if batch_id in active_batches:
        return JsonResponse(active_batches[batch_id])
    else:
        # Check if it's a completed batch file
        batches = get_batch_files()
        for batch in batches:
            if batch['batch_id'] == batch_id:
                return JsonResponse({
                    'status': 'completed',
                    'current_stage': 'Completed',
                    'articles_scraped': batch['article_count']
                })
        
        return JsonResponse({
            'status': 'not_found',
            'error': 'Batch not found'
        }, status=404)

@login_required
@user_passes_test(admin_required)
def download_batch(request, batch_id):
    """Download a batch CSV file"""
    try:
        batches = get_batch_files()
        batch_file = None
        
        for batch in batches:
            if batch['batch_id'] == batch_id:
                batch_file = batch['file_path']
                break
        
        if not batch_file or not os.path.exists(batch_file):
            raise Http404("Batch file not found")
        
        with open(batch_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="news_scrape_{batch_id}.csv"'
            return response
            
    except Exception as e:
        messages.error(request, f"Error downloading batch: {str(e)}")
        return redirect('news:admin_list_batches')

@login_required
@user_passes_test(admin_required)
@require_POST
def delete_batch(request, batch_id):
    """Delete a batch CSV file"""
    try:
        batches = get_batch_files()
        batch_file = None
        
        for batch in batches:
            if batch['batch_id'] == batch_id:
                batch_file = batch['file_path']
                break
        
        if batch_file and os.path.exists(batch_file):
            os.remove(batch_file)
            
            # Remove from active batches if exists
            if batch_id in active_batches:
                del active_batches[batch_id]
            if batch_id in batch_results:
                del batch_results[batch_id]
            
            return JsonResponse({
                'success': True,
                'message': f'Batch {batch_id} deleted successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Batch file not found'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@user_passes_test(admin_required)
def view_batch_content(request, batch_id):
    """View contents of a batch CSV file"""
    try:
        batches = get_batch_files()
        batch_file = None
        batch_info = None
        
        for batch in batches:
            if batch['batch_id'] == batch_id:
                batch_file = batch['file_path']
                batch_info = batch
                break
        
        if not batch_file or not os.path.exists(batch_file):
            raise Http404("Batch file not found")
        
        # Read CSV data
        df = pd.read_csv(batch_file)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        per_page = 50
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_data = df[start_idx:end_idx]
        total_pages = (len(df) + per_page - 1) // per_page
        
        # Convert to template-friendly format with column names
        rows_data = []
        for _, row in paginated_data.iterrows():
            row_dict = {}
            for col in df.columns:
                # Clean column names for template access
                clean_col = col.replace(' ', '_').replace('-', '_').lower()
                row_dict[clean_col] = row[col] if pd.notna(row[col]) else ''
                row_dict[f'col_{clean_col}'] = col  # Store original column name
            rows_data.append(row_dict)
        
        # Also create a simple list format for easier iteration
        simple_rows = []
        for _, row in paginated_data.iterrows():
            row_values = []
            for col in df.columns:
                row_values.append(row[col] if pd.notna(row[col]) else '')
            simple_rows.append(row_values)
        
        context = {
            'batch_info': batch_info,
            'data': simple_rows,
            'columns': df.columns.tolist(),
            'current_page': page,
            'total_pages': total_pages,
            'total_records': len(df),
            'has_previous': page > 1,
            'has_next': page < total_pages,
            'previous_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
        
        return render(request, 'admin_scraper/view_batch.html', context)
        
    except Exception as e:
        messages.error(request, f"Error viewing batch: {str(e)}")
        return redirect('news:admin_list_batches')