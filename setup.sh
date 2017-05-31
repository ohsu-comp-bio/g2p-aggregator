#!/bin/bash
echo install and configure app

#
echo checking docker compose alias
if [ `alias | grep dc | wc -l` != 1 ]; then

echo Please configure environmental variables
echo
echo e.g. for standalone development ...
cat <<EOT
  alias dc='docker-compose -f docker-compose.yml'
  export SERVER_NAME=g2p-ohsu.ddns.net
  export ADMIN_EMAIL=walsbr@ohsu.edu
EOT
echo
echo e.g. for cloud depoyment ...
cat <<EOT
  alias dc='docker-compose -f docker-compose.yml -f cloud-setup/docker-compose-nginx.yml'
  export SERVER_NAME=g2p-ohsu.ddns.net
  export ADMIN_EMAIL=walsbr@ohsu.edu
EOT
exit 1
fi


#
echo checking clone repo
if [ ! -d ~/g2p-aggregator ]; then
  # clone repo
  cd ~
  git clone https://github.com/ohsu-comp-bio/g2p-aggregator.git
  cd g2p-aggregator
  cat <<EOT > .env
ELASTIC_PORT=9200
KIBANA_PORT=5601
EOT

fi


echo checking backup dir
if [ ! -d ~/g2p-aggregator/util/elastic/backups ]; then
  echo copy snapshot back up to this host... e.g.
  echo scp -r -i [your key] ~/g2p-aggregator/util/elastic/backups/ [user]@[host]:g2p-aggregator/util/elastic/backups
  mkdir ~/g2p-aggregator/util/elastic/backups
fi


if [ -d ~/g2p-aggregator/util/elastic/backups ]; then
  cd ~/g2p-aggregator
  dc up -d
fi
