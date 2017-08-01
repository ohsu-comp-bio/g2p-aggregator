#!/bin/bash

# setup elastic search
if [ -z "$1" ]
  then
    ES=http://localhost:9200
  else
    ES=$1
fi

TS=$(date +"%Y%m%dt%H%M")

curl -XPUT $ES'/_snapshot/backups/snapshot_'$TS'?wait_for_completion=true&pretty' -d'
{
  "indices": ".kibana,associations-new",
  "ignore_unavailable": true,
  "include_global_state": false
}'
