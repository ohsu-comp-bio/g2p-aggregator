# elasticsearch-react
An example project showing how to use Elasticsearch with React

## Prerequisites

To run this example, you will need to configure Elasticsearch (or nginx) to accept requests from the browser using [CORS](http://en.wikipedia.org/wiki/Cross-origin_resource_sharing).


To enable CORS, add the following to Elasticsearch's config file. Usually, this file is located near the elasticsearch executable at `config/elasticsearch.yml`. [source](https://github.com/spalger/elasticsearch-angular-example)

## To build the example:
1. Clone this repo locally (or just download and unzip it)

 ```sh
 docker build  -f build.dockerfile -t ui-builder  .
 docker run -it -v $(pwd):/ui ui-builder cp /node/index.js /ui/index.js
 ``` 

2. Testing

  ```sh
  python -m  SimpleHTTPServer
  ```

3. Deploy

  see nginx mapping
