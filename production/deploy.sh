#!/bin/bash
set -e

echo '----- 1. Pulling code updates from GitHub...'
git pull

echo '----- 2. Starting containers...'
docker compose -f docker-compose.prod.yaml down
docker compose -f docker-compose.prod.yaml up -d --build

echo "----- 3. Collecting static files... -----"
docker compose -f docker-compose.prod.yaml exec backend python manage.py collectstatic --noinput
echo "Static files collected."

echo '----- 4. Deploy completed!'
