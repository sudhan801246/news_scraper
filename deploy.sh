#!/bin/bash
set -e

echo "🚀 Starting Railway deployment..."

cd app

echo "📊 Checking database connection..."
python manage.py check --database default

echo "🗃️ Running database migrations..."
python manage.py migrate --noinput --verbosity=2

echo "🗂️ Collecting static files..."
python manage.py collectstatic --noinput

echo "📰 Loading news data if database is empty..."
python manage.py load_news_data --info || echo "Data loading skipped"

echo "✅ Deployment completed successfully!"