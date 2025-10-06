from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Debug database connection and show current state'
    
    def handle(self, *args, **options):
        self.stdout.write("🔍 Database Debug Information")
        self.stdout.write("=" * 50)
        
        # Show database settings
        db_settings = settings.DATABASES['default']
        self.stdout.write(f"Engine: {db_settings['ENGINE']}")
        self.stdout.write(f"Name: {db_settings.get('NAME', 'Not set')}")
        self.stdout.write(f"Host: {db_settings.get('HOST', 'Not set')}")
        self.stdout.write(f"Port: {db_settings.get('PORT', 'Not set')}")
        self.stdout.write(f"User: {db_settings.get('USER', 'Not set')}")
        
        # Show environment variables
        self.stdout.write("\n📋 Environment Variables:")
        self.stdout.write(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
        self.stdout.write(f"DEBUG: {os.environ.get('DEBUG', 'NOT SET')}")
        
        # Test database connection
        self.stdout.write("\n🔌 Testing Database Connection:")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                self.stdout.write(f"✅ Connected to: {version}")
                
                # Check if auth_user table exists
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'auth_user'
                """)
                auth_table = cursor.fetchone()
                
                if auth_table:
                    self.stdout.write("✅ auth_user table EXISTS")
                    
                    # Count users
                    cursor.execute("SELECT COUNT(*) FROM auth_user")
                    user_count = cursor.fetchone()[0]
                    self.stdout.write(f"👥 Users in database: {user_count}")
                else:
                    self.stdout.write("❌ auth_user table MISSING")
                
                # List all tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                self.stdout.write(f"\n📊 All tables ({len(tables)}):")
                for table in tables:
                    self.stdout.write(f"  - {table[0]}")
                    
        except Exception as e:
            self.stdout.write(f"❌ Database connection failed: {e}")
            
        # Check migration status
        self.stdout.write("\n🗃️ Migration Status:")
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                self.stdout.write(f"⚠️ Pending migrations: {len(plan)}")
                for migration, backwards in plan:
                    self.stdout.write(f"  - {migration}")
            else:
                self.stdout.write("✅ All migrations applied")
                
        except Exception as e:
            self.stdout.write(f"❌ Could not check migrations: {e}")
            
        self.stdout.write("\n" + "=" * 50)