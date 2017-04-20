
# Integration Tests

## Code Generation

### move to tests directory
```
cd  tests/integration/
```

### install schema management

```
pip install git+https://github.com/ohsu-computational-biology/bioschemas
```


### get the schema
```
bioschemas-snapshot -o ga4gh
```

### generate ga4gh python code into folder ./ga4gh
```
protoc --proto_path=bioschemas/proto/ga4gh  --python_out=. bioschemas/proto/ga4gh/ga4gh/*.proto
```
### generate ohsu python code into folder ./oshu

```
protoc --proto_path=bioschemas/proto \
       --proto_path=bioschemas/proto/ga4gh \
       --proto_path=bioschemas/proto/ohsu \
       --python_out=. \
       bioschemas/proto/ohsu/g2p.proto
 ```

### use the code
```
>>> import sys
>>> sys.path.append(os.getcwd() + '/tests/integration')  # NOQA
>>> from ga4gh import genotype_phenotype_pb2 as g2p
```
