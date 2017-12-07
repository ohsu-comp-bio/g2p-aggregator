#!/bin/bash

# setup elastic search
if [ -z "$ES" ]
  then
    ES=http://localhost:9200
fi
echo setting up $ES
curl  -X DELETE $ES"/associations-new"
echo deleted

# shards disk.indices disk.used disk.avail disk.total disk.percent host      ip        node
#     21        9.7gb    20.4gb     42.2gb     62.7gb           32 127.0.0.1 127.0.0.1 -BRXEWH
#     21                                                                               UNASSIGNED

# curl -XPUT $ES"/associations-new" -H 'Content-Type: application/json' -d'
# {
#   "settings" : {
#       "index" : {
#         "mapping.total_fields.limit": 30000
#       }
#   },
#
#   "mappings": {
#     "association": {
#       "dynamic_templates": [
#         {
#           "strings": {
#             "match_mapping_type": "string",
#             "mapping": {
#               "type": "text",
#               "fields": {
#                 "keyword": {
#                   "type":  "keyword",
#                   "ignore_above": 1024,
#                   "store": true
#                 }
#               }
#             }
#           }
#         }
#       ]
#     }
#   }
# }'
echo created

curl -XPUT $ES"/associations-new" -H 'Content-Type: application/json' -d'
{
  "settings":{
    "index":{
      "mapping.total_fields.limit":30000
    }
  },
  "mappings":{
    "association":{
      "properties":{
        "civic":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "cgi":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "oncokb":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "jax":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "pmkb":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "molecularmatch":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "sage":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "jax_trials":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "brca":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        },
        "molecularmatch_trials":{
          "type":"keyword",
          "store":true, "index":false, "ignore_above":0
        }
      },
      "dynamic_templates":[
        {
          "strings":{
            "match_mapping_type":"string",
            "mapping":{
              "type":"text",
              "fields":{
                "keyword":{
                  "type":"keyword",
                  "ignore_above":1024,
                  "store":true
                }
              }
            }
          }
        }
      ]
    }
  }
}
'
echo created


# curl  -X PUT $ES"/associations-new/_settings" -d'
# {
#   "index.mapping.total_fields.limit": 30000
# }'
# echo settings
#
# curl  -X PUT $ES"/associations-new" -d'
# {
#     "settings" : {
#         "index" : {
#           "mapping.total_fields.limit": 30000
#         }
#     }
# }
# '
# echo created

curl -XPOST  $ES"/_aliases" -H 'Content-Type: application/json' -d'
{
    "actions" : [
        { "add" : { "index" : "associations-new", "alias" : "associations" } }
    ]
}'
echo aliased
