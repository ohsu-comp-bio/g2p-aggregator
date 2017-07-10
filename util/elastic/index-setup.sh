#!/bin/bash

# setup elastic search
if [ -z "$1" ]
  then
    ES=http://localhost:9200
  else
    ES=$1
fi

curl  -X DELETE $ES"/associations-new"
echo deleted

curl -XPUT $ES"/associations-new" -H 'Content-Type: application/json' -d'
{
  "settings" : {
      "index" : {
        "mapping.total_fields.limit": 30000
      }
  },

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
                  "ignore_above": 1024,
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
echo created


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
#               "fielddata":true
#             }
#           }
#         }
#       ]
#     }
#   }
# }'
# echo created


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
