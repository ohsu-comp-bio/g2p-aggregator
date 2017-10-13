# notebook 

## external dependencies
  https://www.synapse.org/#!Synapse:syn7851250 copy to data_mutations_extended_1.0.1.txt
  make available to your notebook environment

## docker integration
  ```docker-compose -f docker-compose.yml -f docker-compose-jupyter.yml up -d```
  * creates a docker instance at port 8888
  * util/ mapped to `/util`
  * elastic search host available at `elastic:9200`
