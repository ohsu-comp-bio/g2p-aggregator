#!/usr/bin/python
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch.helpers import bulk

import json
import os
import argparse
import sys


def _stdin_actions(index):
    for line in sys.stdin:
        hit = json.loads(line)
        hit = _del_source(hit)
        yield {
            '_index': index,
            '_op_type': 'index',
            '_type': 'association',
            '_source': hit
        }


def _del_source(hit):
    """ we have stored some fields as json strings, convert back to obj"""
    sources = set(['cgi', 'jax', 'civic', 'oncokb', 'molecularmatch_trials',
                   'molecularmatch', 'pmkb', 'sage', 'brca', 'jax_trials'])
    props = set(hit.keys())
    source = sources.intersection(props)
    if len(source) == 1:
        source = list(source)[0]
        del hit[source]
    return hit


# Use DSL to query genomic location, subset of fields,
def _from_stdin(index='associations-snapshot'):
    # get connection info from env
    HOST = [os.environ.get('ES', 'localhost:9200')]
    client = Elasticsearch(HOST)
    # validate connection
    assert(client.info()['version'])
    print 'writing to ', index, HOST
    # write to ES
    print bulk(client, (d for d in _stdin_actions(index)))

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--index',
                           help='write stdin to index',
                           )
    args = argparser.parse_args()
    _from_stdin(args.index)
