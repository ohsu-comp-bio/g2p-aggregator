#  Setup dms-dev.compbio.ohsu.edu

## first: clone git

`git clone git@github.com:ohsu-comp-bio/g2p-aggregator.git`

## second: docker setup

* ensure docker is clean
  `docker ps` should return no unexpected results
* setup alias
  `alias dc='docker-compose -f docker-compose.yml -f cloud-setup/docker-compose-nginx.yml'`
* setup local certs file (certs is _not_ checked into git)
  ```
  $ cd ~/g2p-aggregator
  $ mkdir certs
  $ cd certs
  # ... create fullchain.pem and privkey.pem
  ```
* setup basic auth password file  (htpasswd is _not_ checked into git)

  edit `services/nginx/.htpasswd`

* change nginx host name
  ```
   diff --git a/services/nginx/nginx_authorize_by_lua.conf b/services/nginx/nginx_authorize_by_lua.conf
   index d4cec33..bb1541c 100644
   --- a/services/nginx/nginx_authorize_by_lua.conf
   +++ b/services/nginx/nginx_authorize_by_lua.conf
   @@ -36,7 +36,7 @@ http {
      # redirect users to https
      server {
        listen                          80;
   -    server_name                     g2p-ohsu.ddns.net;  # change this to your host
   +    server_name                     dms-dev.compbio.ohsu.edu;  # change this to your host
        location / {
          return 301                    https://$server_name$request_uri;
        }
   @@ -45,7 +45,7 @@ http {
      # all access via https
      server {
        listen                          443 ssl;
   -    server_name                     g2p-ohsu.ddns.net; # change this to your host
   +    server_name                     dms-dev.compbio.ohsu.edu; # change this to your host
        # certs
        ssl_certificate                 /certs/fullchain.pem;
        ssl_certificate_key             /certs/privkey.pem;
  ```       

* start docker
  `$ dc up -d`

* verify docker start

```
$ docker ps
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS              PORTS                                      NAMES
6b3373081bab        openresty/openresty:trusty   "/usr/local/openresty"   43 minutes ago      Up 29 minutes       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   nginx_g2p
c5b1b3d702fc        g2paggregator_kibana         "/bin/sh -c /usr/loca"   43 minutes ago      Up 43 minutes       0.0.0.0:5601->5601/tcp                     kibana_g2p
9a9d767aafb7        g2paggregator_elastic        "/bin/bash bin/es-doc"   43 minutes ago      Up 43 minutes       0.0.0.0:9200->9200/tcp, 9300/tcp           elastic_g2p
```


## third: restore / create elastic search indices
  * You may want to restore elastic indices from another instance.
  * The ES instance running in docker, has a `backups` snapshot repo set for the file system at util/elastic/backups (this is _not_ checked into git). See [ES Documentation for more](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-snapshots.html). There are sample commands checked into git at `util/elastic/*.sh`
  * Alternatively, run harvesters to recollect data. (And restore kibana visualizations/dashboards)

## functionality in Internet Explorer
  * In order for Internet Explorer to run g2p according to this set-up, after initialization, go to `dms-dev.compbio.ohsu.edu/kibana` and click on 'management/avanced settings`. The option `state:InSessionStorage` must be set to true and saved. 
