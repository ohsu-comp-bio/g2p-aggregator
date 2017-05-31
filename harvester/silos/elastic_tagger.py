from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import json
import sys

# module level funtions


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def populate_args(argparser):
    """add arguments we expect """
    argparser.add_argument('--elastic_search', '-es',
                           help='''elastic search endpoint''',
                           default='localhost')

    argparser.add_argument('--elastic_index', '-i',
                           help='''elastic search index''',
                           default='associations-new')

    argparser.add_argument('--genes',   nargs='+',
                           help='array of hugo ids')

    argparser.add_argument('--query',
                           help='elastic query string')

    argparser.add_argument('--tag_property', required=True,
                           help='name of tag container',
                           default="tags")

    argparser.add_argument('--tag_name', required=True,
                           help='tag name')


class ElasticTagger:
    """ A tagger updates documents with a tag"""
    ANY_QUERY = {
        "query": {
            "simple_query_string": {
               "query": None
            }
        },
        "script": {
            "inline": "ctx._source.{}.add(params.tag)",
            "params": {
                "tag": None
            },
            "lang": "painless"
         }
    }

    GENE_QUERY = {
     "query": {
       "wildcard": {
           "gene.keyword": None
       }
     },
     "script": {
      "inline": "ctx._source.{}.add(params.tag)",
      "params": {
       "tag": None
      },
      "lang": "painless"
     }
    }

    def __init__(self, args):
        """ initialize, set endpoint & index name """
        self._es = Elasticsearch([args.elastic_search])
        self._index = args.elastic_index
        self._genes = args.genes
        self._tag_property = args.tag_property
        self._tag_name = args.tag_name
        self._query = args.query

    def __str__(self):
        return "ElasticTagger es:{} i:{} g:{} p:{} n:{}" \
               .format(self._es,
                       self._index,
                       self._genes,
                       self._tag_property,
                       self._tag_name)

    def _update_by_genes(self):
        q = None
        try:
            for gene in self._genes:
                q = self.GENE_QUERY
                q['query']['wildcard']['gene.keyword'] = gene
                q['script']['params']['tag'] = self._tag_name
                q['script']['inline'] = q['script']['inline'].format(self._tag_property)  # NOQA
                self._es.update_by_query(index=self._index, body=q)
        except Exception as e:
            _eprint(e)
            _eprint(json.dumps(q))
            pass

    def _update_by_query(self):
        q = None
        try:
            q = self.ANY_QUERY
            q['query']['simple_query_string']['query'] = self._query
            q['script']['params']['tag'] = self._tag_name
            q['script']['inline'] = q['script']['inline'].format(self._tag_property)  # NOQA
            self._es.update_by_query(index=self._index, body=q)
        except Exception as e:
            _eprint(e)
            _eprint(json.dumps(q))
            pass

    def tag_all(self):
        """ update matching documents """
        if self._genes:
            self._update_by_genes()
        if self._query:
            self._update_by_query()
