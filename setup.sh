echo install & configure app
# for github access
if [ ! -f ~/g2p-aggregator ]; then
  # clone repo
  cd ~
  git clone https://github.com/ohsu-comp-bio/g2p-aggregator.git
  cd g2p-aggregator
  cat <<EOT > .env
ELASTIC_PORT=9200
KIBANA_PORT=5601
EOT

  alias dc=docker-compose
  dc up -d
fi


if [ ! -f ~/g2p-aggregator/util/elastic/backups ]; then
  echo copy snapshot back up to this host... e.g.
  echo scp -r -i [your key] ~/g2p-aggregator/util/elastic/backups/ [user]@[host]:g2p-aggregator/util/elastic/backups
  mkdir ~/g2p-aggregator/util/elastic/backups
fi


if [ -f ~/g2p-aggregator/util/elastic/backups ]; then
  cd ~/g2p-aggregator
  alias dc=docker-compose
  dc up -d
fi
