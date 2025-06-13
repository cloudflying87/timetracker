#!/usr/bin/env python3
"""
Setup script for TimeTracker Django application
"""

import os
import django
from django.core.management import execute_from_command_line

def setup_environment():
    """Set up Django environment"""
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetracker.settings')
        django.setup()
    except ImportError as e:
        print(f"❌ Error importing dependencies: {e}")
        print("Please install required packages:")
        print("pip install python-decouple psycopg2-binary")
        exit(1)

def create_initial_data():
    """Create initial data for the application"""
    from timetrack.models import HourLimit
    from django.contrib.auth.models import User
    
    # Create hour limits if they don't exist
    if not HourLimit.objects.filter(period='weekly').exists():
        HourLimit.objects.create(period='weekly', max_hours=40)
        print("✓ Created weekly hour limit (40 hours)")
    
    if not HourLimit.objects.filter(period='monthly').exists():
        HourLimit.objects.create(period='monthly', max_hours=160)
        print("✓ Created monthly hour limit (160 hours)")
    
    print("\n✓ Initial setup completed!")
    print("\nNext steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Set pay rates for users in the admin panel")
    print("3. Start tracking time!")

def main():
    """Main setup function"""
    print("🕐 Setting up TimeTracker...")
    
    # Set up Django environment
    setup_environment()
    
    # Run migrations
    print("\n📦 Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Collect static files
    print("\n📂 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    # Create initial data
    print("\n🔧 Creating initial data...")
    create_initial_data()

if __name__ == '__main__':
    main()