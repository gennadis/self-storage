#!/bin/bash

read -p "Enter your domain address: (example.com) " domain
read -p "Enter your email address: " email
read -p "Staging: 1 - test, 0 - deploy : " staging

rsa_key_size=4096
data_path="./data/certbot"

if [ -d "$data_path" ]; then
    read -p "Existing data found for $domain. Continue and replace existing certificate? (y/N) " decision
    if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
        exit
    fi
fi

if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
    echo "### Downloading recommended TLS parameters ..."
    mkdir -p "$data_path/conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf >"$data_path/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem >"$data_path/conf/ssl-dhparams.pem"
    echo
fi

echo "### Removing old certificate for $domain ..."
docker-compose -f docker-compose.prod.yaml run --rm --entrypoint "\
rm -Rf /etc/letsencrypt/live/$domain && \
rm -Rf /etc/letsencrypt/archive/$domain && \
rm -Rf /etc/letsencrypt/renewal/$domain.conf" certbot
echo


echo "### Creating dummy certificate for $domain ..."
path="/etc/letsencrypt/live/$domain"
mkdir -p "$data_path/conf/live/$domain"
docker-compose -f docker-compose.prod.yaml run --rm --entrypoint "\
openssl req -x509 -nodes -newkey rsa:1024 -days 1 \
-keyout "$path/privkey.pem" \
-out "$path/fullchain.pem" \
-subj '/CN=localhost'" certbot
echo


echo "### Starting nginx ..."
docker-compose -f docker-compose.prod.yaml up --force-recreate -d nginx
echo


echo "### Removing dummy certificate for $domain ..."
docker-compose -f docker-compose.prod.yaml run --rm --entrypoint "\
rm -Rf /etc/letsencrypt/live/$domain" certbot
echo


echo "### Requesting Let's Encrypt certificates ..."

# Select appropriate email arg
case "$email" in
"") email_arg="--register-unsafely-without-email" ;;
*) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi


docker-compose -f docker-compose.prod.yaml run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    -d $domain \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo


echo "### Reloading nginx ..."
docker-compose -f docker-compose.prod.yaml exec nginx nginx -s reload