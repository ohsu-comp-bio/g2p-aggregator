#!/usr/bin/python
import sys
import argparse
sys.path.append('silos')  # NOQA

import json
import argparse
import logging
import logging.config
import yaml
import re

import smmart

import drug_normalizer
import disease_normalizer
import oncogenic_normalizer
import biomarker_normalizer

import drug_normalizer
import disease_normalizer
import reference_genome_normalizer

from file_silo import FileSilo
import file_silo

import requests
import requests_cache
import timeit
import hashlib
import location_normalizer

DUPLICATES = []

# cache responses
requests_cache.install_cache('harvester', allowable_codes=(200, 400, 404))

args = None
silos = None


def _make_silos(args):
    """ construct silos """
    silos = []
    for s in args.silos:
        if s == 'file':
            silos.append(FileSilo(args))
    return silos


# cgi, jax, civic, oncokb
def harvest(genes):
    """ get evidence from all sources """
    for h in args.harvesters:
        harvester = sys.modules[h]

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

    start_time = timeit.default_timer()
    # functionality for oncogenic_normalizer already mostly in harvesters
    oncogenic_normalizer.normalize_feature_association(feature_association)
    elapsed = timeit.default_timer() - start_time
    if elapsed > 1:
        logging.info('oncogenic_normalizer {}'.format(elapsed))

    start_time = timeit.default_timer()
    location_normalizer.normalize_feature_association(feature_association)
    elapsed = timeit.default_timer() - start_time
    if elapsed > 1:
        logging.info('location_normalizer {}'.format(elapsed))

    start_time = timeit.default_timer()
    reference_genome_normalizer \
        .normalize_feature_association(feature_association)
    elapsed = timeit.default_timer() - start_time
    if elapsed > 1:
        logging.info('reference_genome_normalizer {}'.format(elapsed))

    start_time = timeit.default_timer()
    biomarker_normalizer.normalize_feature_association(feature_association)
    if elapsed > 1:
        logging.info('biomarker_normalizer {}'.format(elapsed))


def main():
    global args
    global silos
    argparser = argparse.ArgumentParser()

    argparser.add_argument('--harvesters',  nargs='+',
                           help='harvest from these sources. default:[smmart]',
                           default=['smmart'])

    argparser.add_argument('--silos',  nargs='+',
                           help='''save to these silos. default:[file]''',
                           default=['file'],
                           choices=['file'])

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
    logging.info("file_output_dir: %r" % args.file_output_dir)

    silos = _make_silos(args)

    feature_associations = [fa for fa in harvest([])]
    # print [f for f in fa['features'] for fa in feature_associations]
    l = []
    for fa in feature_associations:
        for f in  fa['features']:
            l.append(f)
    print l
    print

    def make_queries(feature_associations):
        # +features.protein_effects:()
        protein_effects = []
        genes = []
        genomic_locations = []
        genomic_starts = []
        protein_domains = []
        pathways = []
        biomarker_types = []
        for fa in feature_associations:
            fa['tags'] = []
            fa['dev_tags'] = []
            normalize(fa)

            for f in fa['features']:
                if 'protein_effects' in f:
                    for pe in f['protein_effects']:
                        protein_effects.append(pe.split(':')[1])

                if 'synonyms' in f:
                    for s in f['synonyms']:
                        is_HG37 = re.compile('NC_.*\.10:g')
                        if is_HG37.match(s):
                            genomic_locations.append(s)

                if 'start' in f:
                    genomic_starts.append({'chromosome': f['chromosome'], 'range': [str(f['start']-i) for i in range(-2,3)]})

                for protein_domain in f.get('protein_domains', []):
                    protein_domains.append(protein_domain['name'])

                for pathway in f.get('pathways', []):
                    pathways.append(pathway)

                if 'sequence_ontology' in f:
                    biomarker_types.append( (f['geneSymbol'], f['sequence_ontology']['name'] ))


            for g in fa['genes']:
                genes.append(g)

        protein_effects = list(set(protein_effects))
        genes = list(set(genes))
        genomic_locations = list(set(genomic_locations))
        protein_domains = list(set(protein_domains))
        pathways = list(set(pathways))
        biomarker_types = list(set(biomarker_types))

        yield '+features.protein_effects:({})'.format(' OR '.join(protein_effects))
        yield '+genes:({})'.format(' OR '.join(genes))
        yield '+features.synonyms.keyword:({})'.format(' OR '.join(['"{}"'.format(g) for g in genomic_locations]))
        yield '+features.protein_domains.name.keyword:({})'.format(' OR '.join(["'{}'".format(d) for d in protein_domains]))
        yield '+features.pathways.keyword:({})'.format(' OR '.join(['"{}"'.format(d) for d in pathways]))



        chromosome_starts = []
        for genomic_start in genomic_starts:
            chromosome_starts.append('(features.chromosome:{} AND features.start:({}))'.format(genomic_start['chromosome'], ' OR '.join(genomic_start['range'])))
        yield ' OR '.join(chromosome_starts)

        biomarker_queries = []
        for t in biomarker_types:
            biomarker_queries.append('(features.geneSymbol:{} AND features.sequence_ontology.name:{})'.format(t[0],t[1]))
        yield ' OR '.join(biomarker_queries)

    def save_bulk(queries):
        q = {
            "query": {
                "query_string": {
                  "analyze_wildcard": True,
                  "default_field": "*",
                  "query": None
                  }
                }
            }
        for query in queries:
            q['query']['query_string']['query'] = query
            print json.dumps(q)
            print

    save_bulk(make_queries(feature_associations))

if __name__ == '__main__':
    main()
