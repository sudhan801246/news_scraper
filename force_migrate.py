#!/usr/bin/env python
"""
Force migration script that runs migrations when the app starts
This ensures migrations run even if Procfile migrations fail
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Add app directory to Python path
sys.path.insert(0, '/app/app')

django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def force_migrate():
    """Force run migrations"""
    print("🚀 Force Migration Script Starting...")
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
        
        # Run migrations
        print("📊 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ Migrations completed!")
        
        # Verify auth_user table exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auth_user'
            """)
            if cursor.fetchone():
                print("✅ auth_user table created successfully!")
            else:
                print("❌ auth_user table still missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

if __name__ == "__main__":
    force_migrate()