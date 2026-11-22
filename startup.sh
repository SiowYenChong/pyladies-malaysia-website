#!/bin/bash
set -e

# Apply database migrations before serving traffic
python manage.py migrate --noinput

# Collect static files so WhiteNoise can serve them when DEBUG=False
python manage.py collectstatic --noinput

# Azure App Service routes traffic to the port in PORT (default 8000)
exec gunicorn config.wsgi --bind=0.0.0.0:${PORT:-8000} --workers 2 --log-file -
