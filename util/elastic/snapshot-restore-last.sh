#!/bin/bash

# setup elastic search
if [ -z "$1" ]
  then
    ES=http://localhost:9200
  else
    ES=$1
fi

SNAPSHOT=`curl -s  $ES'/_snapshot/backups/_all'  | jq -r .snapshots[-1].snapshot`

echo restoring $SNAPSHOT
curl -XPOST  $ES/_all/_close
curl  -XPOST $ES'/_snapshot/backups/'$SNAPSHOT'/_restore'
curl -XPOST  $ES/_all/_open
