from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
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


class ElasticSilo:
    """ A silo is where we store stuff that has been harvested.
        Store features in elastic search"""

    def __init__(self, args):
        """ initialize, set endpoint & index name """
        self._es = Elasticsearch([args.elastic_search])
        self._index = args.elastic_index

    def __str__(self):
        return "ElasticSilo es:{} idx:{}".format(self._es, self._index)

    def delete_all(self):
        """delete index"""
        try:
            indices_client = IndicesClient(self._es)
            indices_client.delete(index=self._index)
        except Exception as e:
            _eprint("exception on delete_index {}".format(e))
            pass

    def delete_source(self, source):
        """ delete source from index """
        try:
            query = {
              "query": {
                "query_string": {
                  "analyze_wildcard": True,
                  "query": "source:{}".format(source)
                }
              }
            }
            self._es.delete_by_query(index=self._index, body=query)
        except Exception as e:
            _eprint(e, query)
            pass

    def save(self, feature_association):
        """ write to es """
        result = self._es.index(index=self._index,
                                body=feature_association,
                                doc_type='association',
                                op_type='index')
        if result['_shards']['failed'] > 0:
            _eprint('failure updating association {}'
                    .format(gene_feature['gene']))
