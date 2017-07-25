#!/bin/bash

# setup elastic search
if [ -z "$1" ]
  then
    ES=http://localhost:9200
  else
    ES=$1
fi


curl -s $ES'/_snapshot/backups/_all' | jq .snapshots[].snapshot
