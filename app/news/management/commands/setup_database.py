from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup database tables and initial data for Railway deployment'
    
    def handle(self, *args, **options):
        self.stdout.write("🚀 Setting up database...")
        
        try:
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.stdout.write("✅ Database connection successful")
            
            # Run migrations
            self.stdout.write("📊 Running migrations...")
            call_command('migrate', verbosity=1, interactive=False)
            self.stdout.write("✅ Migrations completed")
            
            # Create superuser if doesn't exist
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write("👤 Creating superuser...")
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com', 
                    password='admin123'
                )
                self.stdout.write("✅ Superuser created: admin/admin123")
            
            # Load news data
            self.stdout.write("📰 Loading news data...")
            try:
                call_command('load_news_data')
                self.stdout.write("✅ News data loaded")
            except Exception as e:
                self.stdout.write(f"⚠️ News data loading skipped: {e}")
            
            self.stdout.write("🎉 Database setup completed successfully!")
            
        except Exception as e:
            self.stdout.write(f"❌ Error during setup: {e}")
            logger.error(f"Database setup error: {e}")
            raise