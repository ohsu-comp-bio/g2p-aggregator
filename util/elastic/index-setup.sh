#!/bin/bash

# setup elastic search
if [ -z "$ES" ]
  then
    ES=http://localhost:9200
fi
echo setting up $ES
curl  -X DELETE $ES"/associations"
curl  -X DELETE $ES"/associations-new"
echo deleted


curl -XPUT $ES"/associations" -H 'Content-Type: application/json' -d'
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
        },
        "evidence": {
          "properties": {
            "evidenceType": {
              "properties": {
                "id": {
                  "type": "keyword"
                }
              }
            }
          }
        },
        "features": {
          "properties": {
            "protein_domains": {
              "properties": {
                "name": {
                  "type":"keyword"
                }
              }
            }
          }
        },
        "association": {
          "properties": {
            "description": {
              "type": "text"
            }
          }
        }
      },
      "dynamic_templates": [
        {
          "strings_as_keywords": {
            "match_mapping_type": "string",
            "mapping": {
              "type": "keyword"
            }
          }
        }
      ]

    }
  }
}
'
echo created



# curl -XPOST  $ES"/_aliases" -H 'Content-Type: application/json' -d'
# {
#     "actions" : [
#         { "add" : { "index" : "associations-new", "alias" : "associations" } }
#     ]
# }'
# echo aliased
