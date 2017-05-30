#!/bin/bash

# setup elastic search
if [ -z "$1" ]
  then
    ES=http://localhost:9200
  else
    ES=$1
fi


curl  -XPOST $ES'/_snapshot/backups/'$2'/restore
