#!/bin/bash

# setup elastic search
if [ -z "$1" ]
  then
    ES=http://localhost:9200
  else
    ES=$1
fi

curl -XPUT $ES'/_snapshot/backups' -H 'Content-Type: application/json' -d '{
    "type": "fs",
    "settings": {
        "location": "/util/elastic/backups",
        "compress": true
    }
}'
