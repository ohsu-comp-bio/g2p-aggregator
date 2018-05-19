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
import oncogenic_normalizer
import reference_genome_normalizer


import requests
import requests_cache
import timeit
import hashlib
import location_normalizer

DUPLICATES = []

# cache responses
requests_cache.install_cache('harvester', allowable_codes=(200, 400, 404))


def harvest(features):
    """ get evidence from all sources """

    for feature in features:
        features = [feature]
        association = {}
        association['phenotype'] = {
            'description': 'Cancer',
        }

        association['evidence'] = [{
            'description': 'ad-hoc query',
        }]

        feature_association = {
                               'genes': [],
                               'features': features,
                               'association': association,
                               'source': 'ad-hoc',
                               }
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


def to_elastic(queries, all_drugs=False, smmart_drugs=None, all_sources=False, sources=None):
    if not all_drugs and not smmart_drugs:
        smmart_drugs = "+association.environmentalContexts.id:('CID23725625', 'CID56842121', u'CHEMBL3137343', 'CID5330286', 'CID444795', 'CID10184653', 'CID5311', 'CID6442177', 'CID11707110', 'CID25102847', 'CID9823820', 'CID24826799', u'CHEMBL1789844', u'CHEMBL2108738', u'CHEMBL2007641', u'CHEMBL1351', 'CID15951529', 'CID132971', 'CID42611257', 'CID9854073', 'CID6918837', 'CID5291', 'CID3062316', 'CID5329102', 'CID216239', 'CID25126798', 'CID387447', 'CID11625818', 'CID49846579', 'CID5284616', u'CHEMBL1201583', 'CID176870', 'CID2662')"
    if not all_sources and not sources:
        sources = "-source:*trials"
    for query, name in queries:
        if smmart_drugs:
            query = '{} {}'.format(smmart_drugs, query)
        if sources:
            query = '{} {}'.format(sources, query)
        yield {'name': name,
               'query':  {
                   "query": {
                       "query_string": {
                         "analyze_wildcard": True,
                         "default_field": "*",
                         "query": query
                         }
                       }
                   }
               }


def generate(features):

    feature_associations = [fa for fa in harvest(features)]


    def make_queries(feature_associations):
        # +features.protein_effects:()
        protein_effects = []
        genes = []
        genomic_locations = []
        genomic_starts = []
        genomic_ranges = []
        protein_domains = []
        pathways = []
        biomarker_types = []
        for fa in feature_associations:
            fa['tags'] = []
            fa['dev_tags'] = []
            # normalize(fa)

            for f in fa['features']:
                if 'protein_effects' in f:
                    for pe in f['protein_effects']:
                        protein_effects.append(pe.split(':')[1])

                if 'synonyms' in f:
                    for s in f['synonyms']:
                        genomic_locations.append(s)
                        # is_HG37 = re.compile('NC_.*\.10:g')
                        # if is_HG37.match(s):
                        #     genomic_locations.append(s)

                if 'start' in f:
                    genomic_starts.append({'chromosome': f['chromosome'], 'range': [str(f['start']-i) for i in range(-2,3)]})
                    genomic_ranges.append({'chromosome': f['chromosome'], 'start': f['start'], 'end': f['end']})

                for protein_domain in f.get('protein_domains', []):
                    protein_domains.append(protein_domain['name'])

                for pathway in f.get('pathways', []):
                    pathways.append(pathway)

                if 'sequence_ontology' in f:
                    biomarker_types.append( (f['geneSymbol'], f['sequence_ontology']['name'] ))

                genes.append(f['geneSymbol'])

        protein_effects = list(set(protein_effects))
        genes = list(set(genes))
        genomic_locations = list(set(genomic_locations))
        protein_domains = list(set(protein_domains))
        pathways = list(set(pathways))
        biomarker_types = list(set(biomarker_types))

        if len(protein_effects) > 0:
            yield '+features.protein_effects:({})'.format(' OR '.join(protein_effects)), 'protein_effects'
        yield '+genes:({})'.format(' OR '.join(genes)), 'genes'
        if len(genomic_locations) > 0:
            yield '+features.synonyms:({})'.format(' OR '.join(['"{}"'.format(g) for g in genomic_locations])), 'alleles'
        if len(protein_domains) > 0:
            yield '+features.protein_domains.name:({})'.format(' OR '.join(["'{}'".format(d) for d in protein_domains])), 'protein_domains'

        chromosome_starts = []
        for genomic_start in genomic_starts:
            chromosome_starts.append('+features.chromosome:{} +features.start:({})'.format(genomic_start['chromosome'], ' OR '.join(genomic_start['range'])))
        yield ' OR '.join(chromosome_starts), '~location'

        chromosome_ranges = []
        for genomic_range in genomic_ranges:
            chromosome_ranges.append('+features.chromosome:{} +features.start:>={} +features.end:<={}'.format(genomic_range['chromosome'], genomic_range['start'], genomic_range['end'] ))
        yield ' OR '.join(chromosome_ranges), '~range'

        biomarker_queries = []
        for t in biomarker_types:
            biomarker_queries.append('+features.geneSymbol:{} +features.sequence_ontology.name:{}'.format(t[0],t[1]))
        if len(biomarker_queries) > 0:
            yield ' OR '.join(biomarker_queries),  '~biomarker_type'

    response = {'queries': {}, 'feature_associations': feature_associations}
    for q in to_elastic(make_queries(feature_associations)):
        response['queries'][q['name']] = q['query']
    return response
