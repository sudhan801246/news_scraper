from django.core.management.base import BaseCommand
from news.data_loader import DataLoader
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load news data from CSV files in the data directory'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reload all data even if database has articles',
        )
        parser.add_argument(
            '--info',
            action='store_true',
            help='Show information about data directory and files',
        )
    
    def handle(self, *args, **options):
        loader = DataLoader()
        
        if options['info']:
            info = loader.get_data_directory_info()
            self.stdout.write(f"Data Directory: {info['data_directory']}")
            self.stdout.write(f"Directory Exists: {info['directory_exists']}")
            self.stdout.write(f"CSV Files Found: {info['csv_files_count']}")
            
            if info['csv_files']:
                self.stdout.write("CSV Files:")
                for filename in info['csv_files']:
                    self.stdout.write(f"  - {filename}")
            else:
                self.stdout.write("No CSV files found")
            return
        
        try:
            self.stdout.write("Loading news data from CSV files...")
            articles_created = loader.load_all_data()
            
            if articles_created > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully loaded {articles_created} new articles')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No new articles were added')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading data: {e}')
            )
            logger.error(f"Data loading error: {e}")