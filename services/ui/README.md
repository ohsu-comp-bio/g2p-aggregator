# elasticsearch-react
An example project showing how to use Elasticsearch with React

## Prerequisites

To run this example, you will need to configure Elasticsearch to accept requests from the browser using [CORS](http://en.wikipedia.org/wiki/Cross-origin_resource_sharing). To enable CORS, add the following to Elasticsearch's config file. Usually, this file is located near the elasticsearch executable at `config/elasticsearch.yml`. [source](https://github.com/spalger/elasticsearch-angular-example)

```yml
http.cors:
  enabled: true
  allow-origin: /https?:\/\/localhost(:[0-9]+)?/
```

## To run the example:
1. Clone this repo locally (or just download and unzip it)

2. Move into the project

  ```sh
  cd services/ui
  ```

3. Run npm install

  ```sh
  npm install
  ```

4. Run webpack (or webpack-dev-server) to build the index.js source file.

  ```sh
  npm run build
  ```

5. Run a server

  ```sh
  python -m  SimpleHTTPServer
  ```
