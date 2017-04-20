#!/bin/bash

# setup elastic search
if [ -z "$1" ]
  then
    ES=http://localhost:9200
  else
    ES=$1
fi


curl -XPUT $ES"/associations-new" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "association": {
      "dynamic_templates": [
        {
          "strings": {
            "match_mapping_type": "string",
            "mapping": {
              "type": "text",
              "fields": {
                "keyword": {
                  "type":  "keyword",
                  "ignore_above": 256,
                  "store": true
                }
              }
            }
          }
        }
      ]
    }
  }
}'


curl -XPOST  $ES"/_aliases" -H 'Content-Type: application/json' -d'
{
    "actions" : [
        { "add" : { "index" : "associations-new", "alias" : "associations" } }
    ]
}'
