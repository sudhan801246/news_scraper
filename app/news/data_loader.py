import os
import pandas as pd
import glob
from django.conf import settings
from .models import Article
import logging
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class DataLoader:
    """Utility class to load and manage CSV data files"""
    
    def __init__(self):
        # Use Railway persistent storage if available
        if os.path.exists("/app/data"):
            # Railway persistent volume
            self.data_dir = "/app/data"
        else:
            # Local development
            self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.data_dir = os.path.join(self.project_root, "data")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def parse_publication_datetime(self, datetime_str):
        """Parse datetime string from scraped data to Django datetime object"""
        if not datetime_str or pd.isna(datetime_str) or str(datetime_str).strip() == '':
            return None
        
        try:
            # The format from scraper is "6 Oct 2025, 16:42"
            parsed_dt = date_parser.parse(str(datetime_str).strip(), fuzzy=True)
            return parsed_dt
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse datetime '{datetime_str}': {e}")
            return None
    
    def get_all_csv_files(self):
        """Get all CSV files from the data directory"""
        pattern = os.path.join(self.data_dir, "news_scrape_*.csv")
        csv_files = glob.glob(pattern)
        return sorted(csv_files)  # Sort by filename (which includes timestamp)
    
    def load_and_deduplicate_csv_data(self):
        """Load all CSV files and remove duplicates based on link field"""
        csv_files = self.get_all_csv_files()
        
        if not csv_files:
            logger.info("No CSV files found in data directory")
            return pd.DataFrame()
        
        logger.info(f"Found {len(csv_files)} CSV files to process")
        
        # Load all CSV files into a single DataFrame
        all_dataframes = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                logger.info(f"Loaded {len(df)} articles from {os.path.basename(csv_file)}")
                all_dataframes.append(df)
            except Exception as e:
                logger.error(f"Error loading {csv_file}: {e}")
        
        if not all_dataframes:
            logger.warning("No valid CSV data found")
            return pd.DataFrame()
        
        # Combine all dataframes
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        logger.info(f"Combined total: {len(combined_df)} articles")
        
        # Remove duplicates based on 'link' field
        initial_count = len(combined_df)
        deduplicated_df = combined_df.drop_duplicates(subset=['link'], keep='last')
        final_count = len(deduplicated_df)
        
        logger.info(f"Removed {initial_count - final_count} duplicates, {final_count} unique articles remain")
        
        return deduplicated_df
    
    def save_articles_to_database(self, dataframe):
        """Save articles from DataFrame to Django database"""
        if dataframe.empty:
            logger.warning("No articles to save to database")
            return 0
        
        articles_created = 0
        articles_updated = 0
        
        for _, row in dataframe.iterrows():
            try:
                # Parse publication datetime
                published_at = self.parse_publication_datetime(row.get('datetime', ''))
                
                # Check if article already exists
                article, created = Article.objects.get_or_create(
                    url=row['link'],
                    defaults={
                        'title': row['title'],
                        'source': row['source'],
                        'category': row['category'],
                        'image': row.get('image', ''),
                        'published_at': published_at,
                    }
                )
                
                if created:
                    articles_created += 1
                else:
                    # Update existing article if needed
                    article.title = row['title']
                    article.source = row['source']
                    article.category = row['category']
                    article.image = row.get('image', '')
                    # Update published_at only if we have a new datetime and the existing one is None
                    if published_at and not article.published_at:
                        article.published_at = published_at
                    article.save()
                    articles_updated += 1
                    
            except Exception as e:
                logger.error(f"Error saving article {row['title']}: {e}")
        
        logger.info(f"Database update complete: {articles_created} created, {articles_updated} updated")
        return articles_created
    
    def load_all_data(self):
        """Main method to load all CSV data and update database"""
        logger.info("Starting data loading process...")
        
        # Load and deduplicate CSV data
        dataframe = self.load_and_deduplicate_csv_data()
        
        if dataframe.empty:
            logger.info("No data to load")
            return 0
        
        # Save to database
        articles_created = self.save_articles_to_database(dataframe)
        
        logger.info(f"Data loading complete: {articles_created} new articles added")
        return articles_created
    
    def get_data_directory_info(self):
        """Get information about the data directory"""
        csv_files = self.get_all_csv_files()
        
        info = {
            'data_directory': self.data_dir,
            'csv_files_count': len(csv_files),
            'csv_files': [os.path.basename(f) for f in csv_files],
            'directory_exists': os.path.exists(self.data_dir)
        }
        
        return info

def load_news_data():
    """Convenience function to load all news data"""
    loader = DataLoader()
    return loader.load_all_data()