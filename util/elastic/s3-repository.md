# self hosted elastic snapshot setup

see cloud-setup for aws elastic host

#### first install the plugin

```
$ dc exec elastic bash
...
dc exec elastic bin/elasticsearch-plugin install repository-s3
```
##### restart elastic afterwards

`dc restart  elastic`

#### configure
By convention, name the s3 client the same as the repository
```
dc exec elastic bin/elasticsearch-keystore add s3.client.g2p-test-snapshots.access_key
dc exec elastic bin/elasticsearch-keystore add s3.client.g2p-test-snapshots.secret_key
dc restart  elastic

```


see https://www.elastic.co/guide/en/elasticsearch/plugins/current/repository-s3-client.html
```
curl -XPUT $ES'/_snapshot/g2p-test?pretty' -H 'Content-Type: application/json' -d'
{
  "type": "s3",
  "settings": {
    "bucket": "g2p-test-snapshots",
    "client": "g2p-test-snapshots"
  }
}
'
```

#### verify
```
$ curl -s $ES/_cat/repositories?v
id       type
g2p-test   s3
$ export REPOSITORY=g2p-test
```


#### list contents

```
$ curl -s $ES'/_snapshot/'$REPOSITORY'/_all' | jq .snapshots[].snapshot
"snapshot_20171119t1738"
"snapshot_20171128t0102"
"snapshot_20171128t0658"
"snapshot_20171201t1405"
export SNAPSHOT=snapshot_20171201t1405
```



#### restore

```
curl -XPOST $ES'/_snapshot/'$REPOSITORY'/'$SNAPSHOT'/_restore?wait_for_completion=true&pretty' -H 'Content-Type: application/json' -d'
{
  "indices": "associations-new"
}
'
```

#### check status
```
curl -s $ES'/_snapshot/backups/'$SNAPSHOT'/_status' | jq .
curl $ES/_cat/indices?v
curl   $ES/_cat/allocation?v
curl $ES/_cat/recovery?v
```
