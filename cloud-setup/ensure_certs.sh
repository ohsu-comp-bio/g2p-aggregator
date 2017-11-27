#!/bin/bash

if [ ! -f ./docker-compose.yml ]; then
  echo Please run from g2-aggregator home directory
  exit 1
fi

if [ ! -f ./services/nginx/.htpasswd ]; then
  echo Please created the ./services/nginx/.htpasswd file
  exit 1
fi


DC='docker-compose -f docker-compose.yml -f cloud-setup/docker-compose-nginx.yml'

if [ -z "$SERVER_NAME" ]
then
      echo "\$SERVER_NAME is empty.  Please set to the public host IP address. \$export SERVER_NAME=xxxx"
      exit 1
fi

if [ -z "$ADMIN_EMAIL" ]
then
      echo "\$ADMIN_EMAIL is empty.  Please set to the email you wish to send to letsencrypt \$export ADMIN_EMAIL=xxxx"
      exit 1
fi

echo "# ensure certs up to date"

echo "# first, shut off nginx"
$DC stop nginx


echo "# checking with letsencrypt"
docker run -it    --rm    --net host    -v `pwd`/letsencrypt_certs:/etc/letsencrypt    -v `pwd`/letsencrypt_lib:/var/lib/letsencrypt     gzm55/certbot certonly --standalone --text -d $SERVER_NAME --agree-tos -m $ADMIN_EMAIL -n "$@"
if [ $? -eq 0 ]
  then
  echo copy the cert and key
  if sudo [ ! -f letsencrypt_certs/live/$SERVER_NAME/fullchain.pem ]; then
    echo could not find letsencrypt_certs/live/$SERVER_NAME/fullchain.pem
    echo please verify letsencrypt default see http://letsencrypt.readthedocs.io/en/latest/using.html#where-are-my-certificates
    exit 1
  fi
  mkdir -p certs
  sudo cp -r letsencrypt_certs/live/$SERVER_NAME   certs
  sudo cat  letsencrypt_certs/live/$SERVER_NAME/fullchain.pem >  certs/fullchain.pem
  sudo cat  letsencrypt_certs/live/$SERVER_NAME/privkey.pem >  certs/privkey.pem
fi

echo "# restart nginx"
$DC restart  nginx
