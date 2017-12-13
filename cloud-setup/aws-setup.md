#  Setup dms-dev.compbio.ohsu.edu

## preliminary
* see `cloud-setup/install_utilities.sh` for pre-requisites
* setup environment:
```
alias dc='docker-compose -f cloud-setup/docker-compose-nginx-aws.yml'
export ES_HOST=search-YOUR-ES-SERVICE.es.amazonaws.com
export ES=https://search-YOUR-ES-SERVICE.es.amazonaws.com
export SERVER_NAME=YOUR.HOST.NAME
export ADMIN_EMAIL=your@email.com
```
* Also, ensure you have created a user in iam and aws cli is setup and operational
  * i.e. `aws ec2 describe-instances` should work


## first: clone git

`git clone git@github.com:ohsu-comp-bio/g2p-aggregator.git`


## second setup letsencrypt certs

  *  make sure SERVER_NAME & ADMIN_EMAIL are set

  ```
  $ cd ~/g2p-aggregator
  $ cloud-setup/ensure_certs.sh
  $ ls -l certs
# -rw-rw-r-- 1 ec2-user ec2-user 3448 Nov 20 22:37 fullchain.pem
# drwxr-xr-x 2 root     root     4096 Nov 20 22:37 g2p-test.ddns.net
# -rw-rw-r-- 1 ec2-user ec2-user 1704 Nov 20 22:37 privkey.pem
  ```


## third: docker setup

* ensure docker is clean
  `docker ps` should return no unexpected results
* setup alias
  `alias dc='docker-compose  -f cloud-setup/docker-compose-nginx-aws.yml'`

* setup basic auth password file  (htpasswd is _not_ checked into git)
  edit `services/nginx/.htpasswd`

* change nginx host name & aws es endpoint
  ```
  $ git diff services/nginx/nginx_authorize_by_lua-aws.conf
  diff --git a/services/nginx/nginx_authorize_by_lua-aws.conf b/services/nginx/nginx_authorize_by_lua-aws.conf
  index bf43a27..11672a2 100644
  --- a/services/nginx/nginx_authorize_by_lua-aws.conf
  +++ b/services/nginx/nginx_authorize_by_lua-aws.conf
  @@ -36,7 +36,7 @@ http {
     # redirect users to https
     server {
       listen                          80;
   -    server_name                     g2p-XXXXXXX; # change this to your host
   +    server_name                     YOUR.NAME.HERE; # change this to your host
       location / {
         return 301                      https://$server_name$request_uri;
       }
  @@ -45,7 +45,7 @@ http {
     # all access via https
     server {
       listen                          443 ssl;
  -    server_name                     g2p-XXXXXXX; # change this to your host
  +    server_name                     YOUR.NAME.HERE; # change this to your host
       # certs
       ssl_certificate                 /certs/fullchain.pem;
       ssl_certificate_key             /certs/privkey.pem;
  @@ -87,7 +87,7 @@ http {

       # asked for elastic search
       location / {
  -      proxy_pass                              http://search-XXXXXXX.es.amazonaws.com;
  +      proxy_pass                              https://search-YOUR-ES-SERVICE.es.amazonaws.com;
         proxy_buffering                         off;
         proxy_pass_request_headers              on;
         proxy_set_header Authorization          "";

  ```       

* ensure that nginx uses correct configuration

```
$ git diff  cloud-setup/docker-compose-nginx.yml
diff --git a/cloud-setup/docker-compose-nginx.yml b/cloud-setup/docker-compose-nginx.yml
index 3a0b059..8d497eb 100644
--- a/cloud-setup/docker-compose-nginx.yml
+++ b/cloud-setup/docker-compose-nginx.yml
@@ -10,8 +10,8 @@ services:
     image: openresty/openresty:trusty
     volumes:
       - "./util:/util/"
-      - "./services/nginx/nginx_authorize_by_lua.conf:/usr/local/openresty/nginx/conf/nginx.conf:ro"
-      - "./services/nginx/authorize.lua:/usr/local/openresty/nginx/conf/authorize.lua:ro"
+      - "./services/nginx/nginx_authorize_by_lua-aws.conf:/usr/local/openresty/nginx/conf/nginx.conf:ro"
+      - "./services/nginx/authorize-aws.lua:/usr/local/openresty/nginx/conf/authorize.lua:ro"
       - "./services/nginx/.htpasswd:/usr/local/openresty/nginx/conf/.htpasswd"
       - "./certs:/certs"
       - "./services/nginx/g2p.html:/var/www/static-html/g2p.html"
```



* start docker
  `$ dc up -d`

* verify docker start

```
$ docker-compose ps
Name                 Command               State                    Ports
----------------------------------------------------------------------------------------------
beacon_g2p   /bin/sh -c python server.py      Up      0.0.0.0:5000->5000/tcp
nginx_g2p    /usr/local/openresty/bin/o ...   Up      0.0.0.0:443->443/tcp, 0.0.0.0:80->80/tcp
```


## third: restore / create elastic search indices
  * You may want to restore elastic indices from another instance.
  * See http://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-managedomains-snapshots.html
  * First create an iam_role if you haven't already `cloud-setup/create_iam_role`
  * Then export the following:
  export ESTEST_MANUAL_SNAPSHOT_S3_BUCKET=g2p-test-snapshots
  export ESTEST_REGION=us-west-2
  export ESTEST_IAM_MANUAL_SNAPSHOT_ROLE_ARN=arn:aws:iam::XXXX:role/ES_Manual_Snapshot_Role
  export ESTEST_AWS_ACCESS_KEY_ID=XXXX
  export ESTEST_AWS_SECRET_ACCESS_KEY=XXXXX
  export ES_CLUSTER_DNS=XXXXX.es.amazonaws.com
  export ESTEST_MANUAL_SNAPSHOT_ROLENAME=ES_Manual_Snapshot_Role
  export ESTEST_MANUAL_SNAPSHOT_IAM_POLICY_NAME=ES_Manual_Snapshot_IAM_Policy


cat << EOF > /tmp/iam-policy_for_es_snapshot_to_s3.json
 {
     "Version":"2012-10-17",
            "Statement":[{
            "Action":["s3:ListBucket"],
             "Effect":"Allow",
            "Resource":["arn:aws:s3:::$ESTEST_MANUAL_SNAPSHOT_S3_BUCKET"]
        },{
            "Action":[
                 "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "iam:PassRole"
            ],
            "Effect":"Allow",
            "Resource":["arn:aws:s3:::$ESTEST_MANUAL_SNAPSHOT_S3_BUCKET/*"]
        }
    ]
}
EOF



## Functionality in Internet Explorer
  * In order for Internet Explorer to run g2p according to this set-up, after initialization, go to `dms-dev.compbio.ohsu.edu/kibana` and click on 'management/advanced settings'. The option `state:InSessionStorage` must be set to true and saved.
