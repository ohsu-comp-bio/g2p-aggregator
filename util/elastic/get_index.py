#!/usr/bin/python
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import json
import os
import argparse


# Use DSL to query genomic location, subset of fields,
def _to_stdout(index='association'):
    # get connection info from env
    HOST = [os.environ.get('ES', 'localhost:9200')]
    client = Elasticsearch(HOST)
    # validate connection
    assert(client.info()['version'])
    s = Search(using=client, index="associations").params(size=1000)
    for hit in s.scan():
        _de_stringify(hit)
        print json.dumps(hit.to_dict(), separators=(',', ':'))


def _de_stringify(hit):
    """ we have stored some fields as json strings, convert back to obj"""
    sources = set(['cgi', 'jax', 'civic', 'oncokb', 'molecularmatch_trials',
                   'molecularmatch', 'pmkb', 'sage', 'brca', 'jax_trials'])
    props = set(dir(hit))
    source = sources.intersection(props)
    if len(source) == 1:
        source = list(source)[0]
        setattr(hit, source, json.loads(getattr(hit, source)))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--index',
                           help='index to write to stdout',
                           )
    args = argparser.parse_args()
    _to_stdout(args.index)
