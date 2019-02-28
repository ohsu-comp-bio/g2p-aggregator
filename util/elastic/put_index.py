#!/usr/bin/python
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch.helpers import bulk

import hgvs.parser

import json
import os
import argparse
import sys

FIX_COUNTERS = {'feature_end': {},
                'feature_start': {},
                'genes': {},
                }

# expensive resource, create only once
HGVS_PARSER = hgvs.parser.Parser()


def _calculated_fields(hit):
    """ add scripted fields """
    if 'drug_labels' in hit['association']:
        hit["association"]["drug_labels_truncated"] = '{:10.10}'.format(hit['association']['drug_labels'])
        hit["drugs"] = hit['association']['drug_labels']
    if 'phenotypes' in hit['association']:
        hit["diseases"] = ','.join([p.get('term','') for p in hit['association']['phenotypes']])
        hit["association"]["disease_labels_truncated"] = ','.join([p['description'] for p in hit['association']['phenotypes']])
    publications = []
    for e in hit['association']['evidence']:
        if e and 'info' in e and e['info']:
            for p in e.get('info', {}).get('publications', []):
                publications.append(p)
    hit["publications"] = ','.join(publications)
    hit["evidence_label"] = hit['association']['evidence_label']
    hit["response"] = hit['association'].get('response_type', None)
    return hit

def _feature_suffixes(hit):
    """ add scripted feature suffixes """
    for feature in hit['features']:
        hgvs_g = set()
        hgvs_p = set()
        for synonym in feature.get('synonyms', []):
            if not ('g.' in synonym or 'p.' in synonym):
                continue
            try:
                hgvs_variant = HGVS_PARSER.parse_hgvs_variant(synonym)
            except Exception as e:
                print(str(e))
                continue
            if hgvs_variant.type == 'p':
                hgvs_p.add(hgvs_variant.format().split(':')[1])
                hgvs_p.add(hgvs_variant.format(conf={"p_3_letter": False}).split(':')[1])
            if hgvs_variant.type == 'g':
                hgvs_g.add(hgvs_variant.format().split(':')[1])
        feature['hgvs_g_suffix'] = list(hgvs_g)
        feature['hgvs_p_suffix'] = list(hgvs_p)
    return hit

def _stdin_actions(args):
    """ create a index record from std in """
    count = 0
    for line in sys.stdin:
        count = count + 1
        if count > args.skip:
            hit = json.loads(line)
            # hit = _fix_features(hit)
            # hit = _fix_genes(hit)
            hit = _stringify(hit)
            # hit = _del_source(hit)
            hit = _calculated_fields(hit)
            hit = _feature_suffixes(hit)
            yield {
                '_index': args.index,
                '_op_type': 'index',
                '_type': 'association',
                '_source': hit
            }


def _fix_genes(hit):
    """ ensure all genes are arrays """
    if not isinstance(hit['genes'], basestring):
        return hit
    c = FIX_COUNTERS['genes'].get(hit['source'], 0)
    FIX_COUNTERS['genes'][hit['source']] = c + 1
    hit['genes'] = hit['genes'].split(',')
    return hit


def _fix_features(hit):
    """ ensure all features start & ends are ints """
    if 'features' in hit:
        for feature in hit['features']:
            if 'end' in feature and feature['end']:
                if isinstance(feature['end'], basestring):
                    c = FIX_COUNTERS['feature_end'].get(hit['source'], 0)
                    FIX_COUNTERS['feature_end'][hit['source']] = c + 1
                    feature['end'] = int(feature['end'])
            if 'start' in feature and feature['start']:
                if isinstance(feature['start'], basestring):
                    c = FIX_COUNTERS['feature_start'].get(hit['source'], 0)
                    FIX_COUNTERS['feature_start'][hit['source']] = c + 1
                    feature['start'] = int(feature['start'])
    return hit


def _del_source(hit):
    """ we have stored some fields as json strings,remove them from obj"""
    sources = set(['cgi', 'jax', 'civic', 'oncokb', 'molecularmatch_trials',
                   'molecularmatch', 'pmkb', 'sage', 'brca', 'jax_trials'])
    props = set(hit.keys())
    source = sources.intersection(props)
    if len(source) == 1:
        source = list(source)[0]
        del hit[source]
    return hit


def _stringify(hit):
    """ store some fields as json strings, convert from obj"""
    sources = set(['cgi', 'jax', 'civic', 'oncokb', 'molecularmatch_trials',
                   'molecularmatch', 'pmkb', 'sage', 'brca', 'jax_trials'])
    props = set(hit.keys())
    source = sources.intersection(props)
    if len(source) == 1:
        source = list(source)[0]
        hit[source] = json.dumps(hit[source])
    return hit


def _from_stdin(args):
    """ Use DSL to query genomic location, subset of fields, """
    # get connection info from env
    HOST = [os.environ.get('ES', 'localhost:9200')]
    client = Elasticsearch(HOST)
    # validate connection
    assert(client.info()['version'])
    print 'writing to ', args.index, HOST
    # write to ES
    if not args.dry_run:
        print bulk(client,
                   (d for d in _stdin_actions(args)),
                   request_timeout=120
                   )
    else:
        for d in _stdin_actions(args):
            if args.verbose:
                print json.dumps(d)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--index',
                           help='write stdin to index',
                           )
    argparser.add_argument('--dry_run', '-d',
                           help='dry run',
                           default=False,
                           action='store_true')
    argparser.add_argument("-v", "--verbose", help="increase output verbosity",
                           default=False,
                           action="store_true")
    argparser.add_argument('--skip',
                           default=-1,
                           type=int,
                           help='skip these lines before importing',
                           )

    args = argparser.parse_args()
    _from_stdin(args)
    sys.stderr.write(json.dumps(FIX_COUNTERS))
