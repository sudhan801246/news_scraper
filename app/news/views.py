from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import random
import logging

from .models import Article, Comment, Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CommentForm
from .scraper import scrape_all_news
from .gemini_client import gemini_client

logger = logging.getLogger(__name__)


# Home and Landing Views
def home(request):
    """Home page with featured articles"""
    try:
        # Get recent articles from each category
        featured_articles = []
        categories = ['technology', 'economy', 'sports', 'politics', 'lifestyle', 'entertainment']
        
        for category in categories:
            articles = Article.objects.filter(category=category)[:2]
            featured_articles.extend(articles)
        
        context = {
            'featured_articles': featured_articles[:6],
            'total_articles': Article.objects.count(),
        }
        return render(request, 'home.html', context)
    except Exception as e:
        logger.error(f"Error in home view: {e}")
        return render(request, 'home.html', {'featured_articles': []})


# Authentication Views
class CustomLoginView(LoginView):
    """Custom login view with enhanced styling"""
    template_name = 'login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('news:dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            login(request, user)
            return redirect('news:dashboard')
    else:
        form = UserRegisterForm()
    
    return render(request, 'register.html', {'form': form, 'title': 'Register'})


@login_required
def profile(request):
    """User profile view with update functionality"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('news:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Profile'
    }
    return render(request, 'profile.html', context)


# News Views
@login_required
def dashboard(request):
    """User dashboard with personalized content"""
    try:
        # Get user's recent comments to suggest interests
        user_comments = Comment.objects.filter(user=request.user)[:5]
        
        # Get articles from each category
        categories = Article.CATEGORY_CHOICES
        category_articles = {}
        
        for category_code, category_name in categories:
            articles = Article.objects.filter(category=category_code)[:4]
            category_articles[category_code] = {
                'name': category_name,
                'articles': articles
            }
        
        context = {
            'category_articles': category_articles,
            'recent_comments': user_comments,
            'total_articles': Article.objects.count(),
            'user_comment_count': user_comments.count(),
        }
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logger.error(f"Error in dashboard view: {e}")
        return render(request, 'dashboard.html', {'category_articles': {}})


class ArticleListView(ListView):
    """List view for articles with filtering and pagination"""
    model = Article
    template_name = 'category_news.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        category = self.kwargs.get('category')
        if category:
            return Article.objects.filter(category=category)
        return Article.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.kwargs.get('category')
        
        if category:
            category_display = dict(Article.CATEGORY_CHOICES).get(category, category.title())
            context['category'] = category
            context['category_display'] = category_display
            context['title'] = f'{category_display} News'
        else:
            context['title'] = 'All News'
            context['category_display'] = 'All Categories'
        
        return context


class ArticleDetailView(DetailView):
    """Detailed view for individual articles"""
    model = Article
    template_name = 'article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        
        # Get related articles from same source/category
        related_articles = Article.objects.filter(
            Q(source=article.source) | Q(category=article.category)
        ).exclude(id=article.id)[:5]
        
        # Get comments and average rating
        comments = article.comments.all()
        avg_rating = comments.aggregate(Avg('rating'))['rating__avg']
        
        context.update({
            'related_articles': related_articles,
            'comments': comments,
            'avg_rating': round(avg_rating) if avg_rating else 0,
            'comment_form': CommentForm() if self.request.user.is_authenticated else None,
            'title': article.title[:50] + '...' if len(article.title) > 50 else article.title
        })
        
        return context


@login_required
@require_POST
def add_comment(request, pk):
    """Add comment to an article"""
    article = get_object_or_404(Article, pk=pk)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.user = request.user
        comment.save()
        messages.success(request, 'Your comment has been added!')
    else:
        messages.error(request, 'Please correct the errors in your comment.')
    
    return redirect('news:article_detail', pk=pk)


# AI Features Views
@login_required
def news_insights(request, category='all'):
    """Generate AI insights for news articles"""
    try:
        # Get articles based on category
        if category != 'all':
            articles = Article.objects.filter(category=category)[:15]
            category_display = dict(Article.CATEGORY_CHOICES).get(category, category.title())
        else:
            # Get a mix from all categories
            articles = list(Article.objects.all()[:20])
            random.shuffle(articles)
            articles = articles[:15]
            category_display = 'All Categories'
        
        if not articles:
            context = {
                'category': category,
                'category_display': category_display,
                'insights': 'No articles available for analysis.',
                'success': False,
                'articles': []
            }
            return render(request, 'insights.html', context)
        
        # Format articles for AI analysis
        headlines = [
            {
                'title': article.title,
                'source': article.source or 'Unknown Source'
            }
            for article in articles
        ]
        
        # Generate insights using Gemini AI
        insights_result = gemini_client.generate_insights(headlines)
        
        context = {
            'category': category,
            'category_display': category_display,
            'insights': insights_result.get('insights', 'Unable to generate insights.'),
            'success': insights_result.get('success', False),
            'articles': articles,
            'title': f'AI Insights - {category_display}'
        }
        
        return render(request, 'insights.html', context)
        
    except Exception as e:
        logger.error(f"Error in news_insights view: {e}")
        context = {
            'category': category,
            'category_display': 'All Categories',
            'insights': 'Error generating insights. Please try again later.',
            'success': False,
            'articles': []
        }
        return render(request, 'insights.html', context)


@login_required
def personalized_news(request):
    """Generate personalized news recommendations"""
    try:
        # Get user interests from query parameters or profile
        interests = request.GET.get('interests', '').split(',')
        interests = [interest.strip() for interest in interests if interest.strip()]
        
        if not interests:
            # Default interests based on user's comment history
            user_categories = Comment.objects.filter(user=request.user).values_list(
                'article__category', flat=True
            ).distinct()
            interests = list(user_categories) or ['technology', 'economy']
        
        # Get recent articles
        all_articles = list(Article.objects.all()[:30])
        random.shuffle(all_articles)
        
        # Format for AI processing
        headlines = [
            {
                'title': article.title,
                'url': article.url,
                'source': article.source or 'Unknown Source',
                'category': article.category,
                'id': article.id
            }
            for article in all_articles
        ]
        
        # Get AI recommendations
        recommended_headlines = gemini_client.personalize_recommendations(interests, headlines)
        
        # Get the actual article objects
        recommended_articles = []
        for headline in recommended_headlines:
            try:
                article = Article.objects.get(id=headline.get('id'))
                recommended_articles.append(article)
            except Article.DoesNotExist:
                continue
        
        context = {
            'recommended_articles': recommended_articles,
            'interests': interests,
            'title': 'Personalized News'
        }
        
        return render(request, 'personalized.html', context)
        
    except Exception as e:
        logger.error(f"Error in personalized_news view: {e}")
        # Fallback to recent articles
        recent_articles = Article.objects.all()[:10]
        context = {
            'recommended_articles': recent_articles,
            'interests': ['General'],
            'title': 'Personalized News',
            'error': 'AI recommendations unavailable. Showing recent articles.'
        }
        return render(request, 'personalized.html', context)


# Admin/Management Views
@login_required
def refresh_news(request):
    """Manually refresh news articles (admin function)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('news:dashboard')
    
    try:
        # Clear existing articles (optional)
        if request.GET.get('clear') == 'true':
            Article.objects.all().delete()
            messages.info(request, 'Existing articles cleared.')
        
        # Scrape new articles
        scraped_data = scrape_all_news()
        
        if scraped_data:
            # Save to database
            created_count = 0
            for article_data in scraped_data:
                article, created = Article.objects.get_or_create(
                    title=article_data['title'],
                    url=article_data['link'],
                    defaults={
                        'image': article_data.get('image', ''),
                        'source': article_data.get('source', ''),
                        'category': article_data.get('category', 'technology'),
                    }
                )
                if created:
                    created_count += 1
            
            messages.success(request, f'Successfully added {created_count} new articles!')
        else:
            messages.warning(request, 'No new articles found.')
    
    except Exception as e:
        logger.error(f"Error refreshing news: {e}")
        messages.error(request, f'Error refreshing news: {str(e)}')
    
    return redirect('news:dashboard')


# Search functionality
def search_articles(request):
    """Search articles by title, source, or category"""
    query = request.GET.get('q', '').strip()
    articles = []
    
    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) |
            Q(source__icontains=query) |
            Q(category__icontains=query)
        )[:20]
    
    context = {
        'articles': articles,
        'query': query,
        'title': f'Search Results for "{query}"' if query else 'Search Articles'
    }
    
    return render(request, 'search_results.html', context)


# API endpoints for AJAX requests
@login_required
def api_article_summary(request, pk):
    """Get AI summary of an article"""
    try:
        article = get_object_or_404(Article, pk=pk)
        
        # Generate summary using AI
        summary = gemini_client.summarize_article(
            article.title,
            f"Article from {article.source} about {article.category}"
        )
        
        return JsonResponse({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        logger.error(f"Error generating article summary: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to generate summary at this time.'
        })


@login_required 
def api_sentiment_analysis(request):
    """Get sentiment analysis of current news"""
    try:
        recent_articles = Article.objects.all()[:20]
        headlines = [
            {
                'title': article.title,
                'source': article.source or 'Unknown'
            }
            for article in recent_articles
        ]
        
        sentiment_result = gemini_client.analyze_sentiment(headlines)
        return JsonResponse(sentiment_result)
    
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Unable to analyze sentiment at this time.'
        })


def debug_database(request):
    """Debug database connection and migration status"""
    from django.http import HttpResponse
    from django.db import connection
    from django.conf import settings
    import os
    
    debug_info = []
    debug_info.append("🔍 DATABASE DEBUG INFORMATION")
    debug_info.append("=" * 50)
    
    # Database settings
    db_settings = settings.DATABASES['default']
    debug_info.append(f"Engine: {db_settings['ENGINE']}")
    debug_info.append(f"Name: {db_settings.get('NAME', 'Not set')}")
    debug_info.append(f"Host: {db_settings.get('HOST', 'Not set')}")
    debug_info.append(f"Port: {db_settings.get('PORT', 'Not set')}")
    debug_info.append(f"User: {db_settings.get('USER', 'Not set')}")
    
    # Environment variables
    debug_info.append("\n📋 ENVIRONMENT VARIABLES:")
    debug_info.append(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
    debug_info.append(f"DEBUG: {os.environ.get('DEBUG', 'NOT SET')}")
    
    # Test database connection
    debug_info.append("\n🔌 DATABASE CONNECTION TEST:")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            debug_info.append(f"✅ Connected to: {version}")
            
            # Check if auth_user table exists
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_user'
            """)
            auth_table = cursor.fetchone()
            
            if auth_table:
                debug_info.append("✅ auth_user table EXISTS")
                cursor.execute("SELECT COUNT(*) FROM auth_user")
                user_count = cursor.fetchone()[0]
                debug_info.append(f"👥 Users in database: {user_count}")
            else:
                debug_info.append("❌ auth_user table MISSING")
            
            # List all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            debug_info.append(f"\n📊 ALL TABLES ({len(tables)}):")
            for table in tables:
                debug_info.append(f"  - {table[0]}")
                
    except Exception as e:
        debug_info.append(f"❌ Database connection failed: {e}")
    
    # Check migration status
    debug_info.append("\n🗃️ MIGRATION STATUS:")
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            debug_info.append(f"⚠️ Pending migrations: {len(plan)}")
            for migration, backwards in plan:
                debug_info.append(f"  - {migration}")
        else:
            debug_info.append("✅ All migrations applied")
            
    except Exception as e:
        debug_info.append(f"❌ Could not check migrations: {e}")
    
    debug_info.append("\n" + "=" * 50)
    
    return HttpResponse("<pre>" + "\n".join(debug_info) + "</pre>", content_type="text/html")