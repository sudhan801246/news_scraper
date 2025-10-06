#!/bin/bash
# Railway release script to run before deployment

cd app

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Loading news data if database is empty..."
python manage.py load_news_data --info

echo "Release script completed successfully!"