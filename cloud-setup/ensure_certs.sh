#!/bin/bash
echo "# ensure certs up to date"
source ~/.bashrc

echo "# first, shut off nginx"
dc stop nginx


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
  sudo cp  letsencrypt_certs/live/$SERVER_NAME   certs
  sudo cat  letsencrypt_certs/live/$SERVER_NAME/fullchain.pem >  certs/fullchain.pem
  sudo cat  letsencrypt_certs/live/$SERVER_NAME/privkey.pem >  certs/privkey.pem
fi

echo "# restart nginx"
docker restart  nginx
