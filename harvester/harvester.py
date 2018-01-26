#!/usr/bin/python
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
import molecularmatch_trials
import pmkb
import drug_normalizer
import disease_normalizer
import oncogenic_normalizer
import biomarker_normalizer
import sage
import brca
import jax_trials

import drug_normalizer
import disease_normalizer
import reference_genome_normalizer

from elastic_silo import ElasticSilo
import elastic_silo
from kafka_silo import KafkaSilo
import kafka_silo
from file_silo import FileSilo
import file_silo

import requests
import requests_cache
import timeit
import hashlib
import location_normalizer

DUPLICATES = []

# cache responses
requests_cache.install_cache('harvester', allowable_codes=(200, 404))


argparser = argparse.ArgumentParser()

argparser.add_argument('--harvesters',  nargs='+',
                       help='''harvest from these sources. default:
                               [cgi_biomarkers,jax,civic,oncokb,
                               pmkb]''',
                       default=['cgi_biomarkers', 'jax', 'civic',
                                'oncokb', 'pmkb', 'brca', 'jax_trials',
                                'molecularmatch_trials'])


argparser.add_argument('--silos',  nargs='+',
                       help='''save to these silos. default:[elastic]''',
                       default=['elastic'],
                       choices=['elastic', 'kafka', 'file'])


argparser.add_argument('--delete_index', '-d',
                       help='''delete all from index''',
                       default=False, action="store_true")

argparser.add_argument('--delete_source', '-ds',
                       help='delete all content for any harvester',
                       default=False, action="store_true")

argparser.add_argument('--genes',   nargs='+',
                       help='array of hugo ids, no value will harvest all',
                       default=None)


argparser.add_argument('--phases',   nargs='+',
                       help='array of harvest phases to run '
                            '[harvest,convert,enrich,all]. default is all',
                       default=['all'],
                       choices=['all', 'harvest'])


elastic_silo.populate_args(argparser)
kafka_silo.populate_args(argparser)
file_silo.populate_args(argparser)


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
logging.info("file_output_dir: %r" % args.file_output_dir)
logging.info("phases: %r" % args.phases)

if not args.genes:
    logging.info("genes: all")
else:
    logging.info("genes: %r" % args.genes)


def is_duplicate(feature_association):
    """ return true if already harvested """
    is_dup = False
    m = hashlib.md5()
    try:
        m.update(json.dumps(feature_association, sort_keys=True))
        hexdigest = m.hexdigest()
        if hexdigest in DUPLICATES:
            is_dup = True
            logging.info('is duplicate {}'.format(
                feature_association['association']['evidence']))
        else:
            DUPLICATES.append(hexdigest)
    except Exception as e:
        logging.warn('duplicate {}'.format(e))
    return is_dup


def _make_silos(args):
    """ construct silos """
    silos = []
    for s in args.silos:
        if s == 'elastic':
            silos.append(ElasticSilo(args))
        if s == 'kafka':
            silos.append(KafkaSilo(args))
        if s == 'file':
            silos.append(FileSilo(args))
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


def harvest_only(genes):
    """ get evidence from all sources """
    for h in args.harvesters:
        harvester = sys.modules[h]
        if args.delete_source:
            for silo in silos:
                if h == 'cgi_biomarkers':
                    h = 'cgi'
                silo.delete_source(h)
        for evidence in harvester.harvest(genes):
            yield {'source': h, h: evidence}


def normalize(feature_association):
    """ standard representation of drugs,disease etc. """
    start_time = timeit.default_timer()

    drug_normalizer.normalize_feature_association(feature_association)
    elapsed = timeit.default_timer() - start_time
    if elapsed > 1:
        environmentalContexts = feature_association['association'].get(
            'environmentalContexts', None)
        logging.info('drug_normalizer {} {}'.format(elapsed,
                                                    environmentalContexts))

    start_time = timeit.default_timer()
    disease_normalizer.normalize_feature_association(feature_association)
    elapsed = timeit.default_timer() - start_time
    if elapsed > 1:
        disease = feature_association['association']['phenotype']['description']
        logging.info('disease_normalizer {} {}'.format(elapsed, disease))

    reference_genome_normalizer \
        .normalize_feature_association(feature_association)
    biomarker_normalizer.normalize_feature_association(feature_association)

    location_normalizer.normalize_feature_association(feature_association)
    # functionality for oncogenic_normalizer already mostly in harvesters
    oncogenic_normalizer.normalize_feature_association(feature_association)


def main():
    if args.delete_index:
        for silo in silos:
            silo.delete_all()

    def _check_dup(harvest):
        for feature_association in harvest:
            feature_association['tags'] = []
            feature_association['dev_tags'] = []
            normalize(feature_association)
            if not is_duplicate(feature_association):
                yield feature_association

    if 'all' in args.phases:
        silos[0].save_bulk(_check_dup(harvest(args.genes)))
    else:
        silos[0].save_bulk(harvest_only(args.genes))


if __name__ == '__main__':
    main()
