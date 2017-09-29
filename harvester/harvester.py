#!/usr/bin/python
from __future__ import print_function
import sys
import argparse
sys.path.append('silos')  # NOQA

import json
import argparse
import logging
import logging.config
import yaml

import jax
import civic
import oncokb
import cgi_biomarkers
import molecularmatch
import pmkb
import drug_normalizer
import disease_normalizer
import sage
import zotero

from elastic_silo import ElasticSilo
import elastic_silo
from kafka_silo import KafkaSilo
import kafka_silo

import requests
import requests_cache
# cache responses
requests_cache.install_cache('harvester')


argparser = argparse.ArgumentParser()

argparser.add_argument('--harvesters',  nargs='+',
                       help='''harvest from these sources. default:
                               [cgi_biomarkers,jax,civic,oncokb,
                               pmkb,zotero]''',
                       default=['cgi_biomarkers', 'jax', 'civic',
                                'oncokb', 'pmkb'])


argparser.add_argument('--silos',  nargs='+',
                       help='''save to these silos. default:[elastic]''',
                       default=['elastic'], choices=['elastic', 'kafka'])


argparser.add_argument('--delete_index', '-d',
                       help='''delete all from index''',
                       default=False, action="store_true")

argparser.add_argument('--delete_source', '-ds',
                       help='delete all content for any harvester',
                       default=False, action="store_true")

argparser.add_argument('--genes',   nargs='+',
                       help='array of hugo ids, no value will harvest all',
                       default=None)


elastic_silo.populate_args(argparser)
kafka_silo.populate_args(argparser)

args = argparser.parse_args()
for h in args.harvesters:
    assert h in sys.modules, "harvester is not a module: %r" % h

path = 'logging.yml'
with open(path) as f:
    config = yaml.load(f)
logging.config.dictConfig(config)


logging.info("harvesters: %r" % args.harvesters)
logging.info("silos: %r" % args.silos)
logging.info("elastic_search: %r" % args.elastic_search)
logging.info("elastic_index: %r" % args.elastic_index)
logging.info("delete_index: %r" % args.delete_index)
if not args.genes:
    logging.info("genes: all")
else:
    logging.info("genes: %r" % args.genes)


def _make_silos(args):
    """ construct silos """
    silos = []
    for s in args.silos:
        if s == 'elastic':
            silos.append(ElasticSilo(args))
        if s == 'kafka':
            silos.append(KafkaSilo(args))
    return silos


silos = _make_silos(args)


# cgi, jax, civic, oncokb
def harvest(genes):
    """ get evidence from all sources """
    for h in args.harvesters:
        harvester = sys.modules[h]
        if args.delete_source:
            for silo in silos:
                if h == 'cgi_biomarkers':
                    h = 'cgi'
                silo.delete_source(h)

        for feature_association in harvester.harvest_and_convert(genes):
            logging.info(
                '{} {} {}'.format(
                    harvester.__name__,
                    feature_association['genes'],
                    feature_association['association']['evidence_label']
                )
            )
            yield feature_association


def normalize(feature_association):
    """ standard representation of drugs,disease etc. """
    drug_normalizer.normalize_feature_association(feature_association)
    disease_normalizer.normalize_feature_association(feature_association)


def main():
    if args.delete_index:
        for silo in silos:
            silo.delete_all()
    for feature_association in harvest(args.genes):
        for silo in silos:
            feature_association['tags'] = []
            feature_association['dev_tags'] = []
            normalize(feature_association)
            silo.save(feature_association)

            # try:
            #     # add tags field for downstream tagger use cases
            #     feature_association['tags'] = []
            #     normalize(feature_association)
            #     silo.save(feature_association)
            # except Exception as e:
            #     logging.info(e)
            #     # logging.info(feature_association)


if __name__ == '__main__':
    main()
