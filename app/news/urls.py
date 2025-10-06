from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import admin_views

app_name = 'news'

urlpatterns = [
    # Home and main pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # News articles
    path('news/', views.ArticleListView.as_view(), name='all_news'),
    path('news/<str:category>/', views.ArticleListView.as_view(), name='category_news'),
    path('article/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<int:pk>/comment/', views.add_comment, name='add_comment'),
    
    # AI Features
    path('insights/', views.news_insights, name='insights'),
    path('insights/<str:category>/', views.news_insights, name='category_insights'),
    path('personalized/', views.personalized_news, name='personalized'),
    
    # Search and utilities
    path('search/', views.search_articles, name='search'),
    path('refresh-news/', views.refresh_news, name='refresh_news'),
    
    # API endpoints
    path('api/article/<int:pk>/summary/', views.api_article_summary, name='api_article_summary'),
    path('api/sentiment/', views.api_sentiment_analysis, name='api_sentiment'),
    
    # Debug endpoints
    path('debug-database/', views.debug_database, name='debug_database'),
    path('force-migrate/', views.force_migrate_now, name='force_migrate'),
    
    # Admin scraper endpoints
    path('admin/scraper/', admin_views.admin_scraper_home, name='admin_scraper_home'),
    path('admin/scraper/batches/', admin_views.list_batches, name='admin_list_batches'),
    path('admin/scraper/start/', admin_views.start_scraping_batch, name='admin_start_scraping'),
    path('admin/scraper/status/<str:batch_id>/', admin_views.batch_status, name='admin_batch_status'),
    path('admin/scraper/view/<str:batch_id>/', admin_views.view_batch_content, name='admin_view_batch'),
    path('admin/scraper/download/<str:batch_id>/', admin_views.download_batch, name='admin_download_batch'),
    path('admin/scraper/delete/<str:batch_id>/', admin_views.delete_batch, name='admin_delete_batch'),
]