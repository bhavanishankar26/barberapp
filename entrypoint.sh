#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate
echo "Starting server..."
exec "$@"