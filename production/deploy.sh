#!/bin/bash
set -e

echo '----- 1. Pulling code updates from GitHub...'
git pull

echo '----- 2. Starting containers...'
docker compose -f docker-compose.prod.yaml down
docker compose -f docker-compose.prod.yaml up -d --build

echo "----- 3. Collecting static files... -----"
docker compose -f docker-compose.prod.yaml exec django python manage.py collectstatic --noinput
echo "Static files collected."

echo '----- 4. Registering deploy on Rollbar...'
ROLLBAR_TOKEN=$(env | grep ROLLBAR_TOKEN | cut -d=   -f2)
REVISION=$(git rev-parse --short HEAD)

curl -s \
     -X POST 'https://api.rollbar.com/api/1/deploy' \
     -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"environment": "production", "revision": "'"$REVISION"'", "rollbar_username": "'"$(whoami)"'", "status": "succeeded"}' \
> /dev/null


echo '----- 5. Deploy completed!'
