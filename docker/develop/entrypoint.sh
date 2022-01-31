#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

cd src

poetry install
poetry run python manage.py makemigrations
poetry run python manage.py migrate
poetry run python manage.py collectstatic --no-input
poetry run python manage.py runserver 0.0.0.0:8000
