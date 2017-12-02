#!/bin/bash

# setup elastic search
if [ -z "$ES" ]
  then
    ES=http://localhost:9200
fi


curl -s $ES'/_snapshot/backups/_all' | jq .snapshots[].snapshot
