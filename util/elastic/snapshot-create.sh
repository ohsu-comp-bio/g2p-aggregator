#!/bin/bash

# setup elastic search
if [ -z "$ES" ]
  then
    ES=http://localhost:9200
fi

if [ -z "$REPOSITORY" ]
  then
    REPOSITORY=$1
fi



TS=$(date +"%Y%m%dt%H%M")

curl -XPUT -H  "Content-Type: application/json" $ES'/_snapshot/'$REPOSITORY'/snapshot_'$TS'?wait_for_completion=true&pretty' -d'
{
  "indices": ".kibana,associations-new",
  "ignore_unavailable": true,
  "include_global_state": false
}'
