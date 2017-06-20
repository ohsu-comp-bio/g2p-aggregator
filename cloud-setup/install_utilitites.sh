echo install utilities on top of aws linux ...
# for command substituton
if [ ! -f /bin/gettext ]; then
  sudo yum  install gettext -y
fi
# jq
if [ ! -f /usr/bin/jq ]; then
  sudo yum install jq -y
fi
# for github access
if [ ! -f /usr/bin/git ]; then
  sudo yum  install git -y
fi

# for docker
if [ ! -f /usr/local/bin/docker-compose ]; then
  sudo sh -c 'curl -L https://github.com/docker/compose/releases/download/1.13.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose'
  sudo chmod +x /usr/local/bin/docker-compose
  sudo usermod -a -G docker ec2-user
fi
