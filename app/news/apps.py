from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        """Called when Django app is ready - load data from CSV files"""
        import news.signals
        
        # Only run this in the main process, not in runserver reloader
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
            
        try:
            from .data_loader import DataLoader
            from .models import Article
            
            # Check if we have any articles in the database
            article_count = Article.objects.count()
            
            if article_count == 0:
                logger.info("No articles found in database, loading from CSV files...")
                loader = DataLoader()
                articles_created = loader.load_all_data()
                
                if articles_created > 0:
                    logger.info(f"Auto-loaded {articles_created} articles from CSV files")
                else:
                    logger.info("No CSV data found to load")
            else:
                logger.info(f"Database already contains {article_count} articles")
                
        except Exception as e:
            logger.error(f"Error auto-loading data: {e}")