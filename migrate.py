#!/usr/bin/env python
"""
Manual migration script for Railway deployment
Run this to create database tables manually
"""

import os
import sys
import django

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("🚀 Starting database migrations...")
    
    try:
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ Migrations completed successfully!")
        
        # Check if superuser exists, create one if not
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("Creating default superuser...")
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("✅ Superuser created: admin/admin123")
        
        print("🎉 Database setup complete!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        sys.exit(1)