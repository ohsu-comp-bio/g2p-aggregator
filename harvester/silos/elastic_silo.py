from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import sys
import json
import logging
from elasticsearch import Elasticsearch, RequestsHttpConnection, \
    serializer, compat, exceptions
from elasticsearch.helpers import bulk

# module level funtions


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
        self._es = Elasticsearch([args.elastic_search],
                                 serializer=JSONSerializerPython2(),
                                 request_timeout=120)
        self._index = args.elastic_index

    def __str__(self):
        return "ElasticSilo es:{} idx:{}".format(self._es, self._index)

    def delete_all(self):
        """delete index"""
        try:
            indices_client = IndicesClient(self._es)
            indices_client.delete(index=self._index)
        except Exception as e:
            logging.error("exception on delete_index {}".format(e))
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
            self._es.delete_by_query(index=self._index,
                                     # doc_type='association',
                                     body=query,
                                     timeout='2m',
                                     request_timeout=120)
            logging.info("deleted associations for {}.{}"
                         .format(self._index, source))
        except exceptions.NotFoundError as nf:
            logging.info("index not found associations for {}.{}"
                         .format(self._index, source))
        except exceptions.ConflictError as ce:
            logging.info("duplicate associations for {}.{}"
                         .format(self._index, source))
        except Exception as e:
            logging.error(query)
            logging.exception(e)
            raise e

    def _stringify_sources(self, feature_association):
        """ Maintaining the original document causes a 'field explosion'
        thousands on fields in a document. So, for now at least,
        maintain it as a string.
        """
        sources = ['cgi', 'jax', 'civic', 'oncokb', 'molecularmatch_trials',
                   'molecularmatch', 'pmkb', 'sage', 'brca', 'jax_trials',
                   'smmart']
        for source in sources:
            if source in feature_association:
                if not isinstance(feature_association[source], basestring):
                    feature_association[source] = json.dumps(feature_association[source])  # NOQA
        return feature_association

    def save(self, feature_association):
        """ write to es """
        # prevent field explosion
        feature_association = self._stringify_sources(feature_association)

        # if 'molecularmatch_trials' in feature_association:
        #     del feature_association['molecularmatch_trials']

        # try:
        result = self._es.index(index=self._index,
                                body=feature_association,
                                doc_type='association',
                                timeout='120s',
                                request_timeout=120,
                                op_type='index'
                                )

        if result['_shards']['failed'] > 0:
            logging.error('failure updating association {}'
                          .format(gene_feature['gene']))
        # except Exception as e:
        #     logging.error(json.dumps(feature_association))
        #     raise e

    def save_bulk(self, feature_association_generator):
        """ write to es """
        # prevent field explosion
        def _bulker(feature_association_generator):
            for feature_association in feature_association_generator:
                feature_association = self._stringify_sources(feature_association)  # NOQA
                yield {
                    '_index': self._index,
                    '_op_type': 'index',
                    '_type': 'association',
                    '_source': feature_association
                }

        result = bulk(self._es,
                      (d for d in _bulker(feature_association_generator)),
                      request_timeout=120)
        logging.info(result)


class JSONSerializerPython2(serializer.JSONSerializer):
    """Override elasticsearch library serializer to ensure it encodes utf characters during json dump.
    See original at: https://github.com/elastic/elasticsearch-py/blob/master/elasticsearch/serializer.py#L42
    A description of how ensure_ascii encodes unicode characters to ensure they can be sent across the wire
    as ascii can be found here: https://docs.python.org/2/library/json.html#basic-usage
    """  # NOQA
    def dumps(self, data):
        # don't serialize strings
        if isinstance(data, compat.string_types):
            return data
        try:
            return json.dumps(data, default=self.default, ensure_ascii=True)
        except (ValueError, TypeError) as e:
            raise exceptions.SerializationError(data, e)
