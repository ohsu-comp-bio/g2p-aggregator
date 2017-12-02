#### first install the plugin

```
$ dc exec elastic bash
...
bin/elasticsearch-plugin install repository-s3
```
##### restart elastic afterwards


#### configure

see https://www.elastic.co/guide/en/elasticsearch/plugins/current/repository-s3-client.html
```
curl -XPUT 'localhost:9200/_snapshot/s3_repository?pretty' -H 'Content-Type: application/json' -d'
{
  "type": "s3",
  "settings": {
    "bucket": "g2p-test-snapshots",
    "region": "us-west-2",
    "access_key": "XXXXX",
    "secret_key": "XXXX"
  }
}
'
```

#### list contents

curl -s $ES'/_snapshot/s3_repository/_all' | jq .snapshots[].snapshot
```
{
  "snapshots": [
    {
      "snapshot": "snapshot_20171119t1738",
      "uuid": "sBahC2UARgKUzHpovlEfSQ",
      "version_id": 5030099,
      "version": "5.3.0",
      "indices": [
        ".kibana",
        "associations-new"
      ],
      "state": "SUCCESS",
      "start_time": "2017-11-20T01:38:11.392Z",
      "start_time_in_millis": 1511141891392,
      "end_time": "2017-11-20T01:38:34.622Z",
      "end_time_in_millis": 1511141914622,
      "duration_in_millis": 23230,
      "failures": [],
      "shards": {
        "total": 6,
        "failed": 0,
        "successful": 6
      }
    }
  ]
}
```


curl -XPOST $ES'/_snapshot/backups/snapshot_20171128t0658/_restore?pretty' -H 'Content-Type: application/json' -d'
{
  "indices": "associations-new"
}

curl -XPOST $ES'/_snapshot/backups/snapshot_20171128t0658/_restore?pretty' -H 'Content-Type: application/json' -d'
{
  "indices": "associations-new"
}
'



curl -XPOST 'localhost:9200/_snapshot/my_backup/snapshot_1/_restore?pretty' -H 'Content-Type: application/json' -d'
{
  "indices": "index_1,index_2",
  "ignore_unavailable": true,
  "include_global_state": true,
  "rename_pattern": "index_(.+)",
  "rename_replacement": "restored_index_$1"
}
'
