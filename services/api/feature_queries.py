import logging
import requests_cache
import re
from harvester import location_normalizer, location_query_generator, \
    biomarker_normalizer
from elasticsearch_dsl import Search, Q

from collections import Counter
import os

DATA_DIR = os.environ.get('HARVESTER_DATA', '../data')

# cache responses
requests_cache.install_cache('{}/harvester'.format(DATA_DIR),
                             allowable_codes=(200, 400, 404))
# our logger
log = logging.getLogger(__name__)


def get_features(args):
    """ harmonize these features"""
    enriched_features = []
    for f in args['features']:
        fa = {'features': [f], 'dev_tags': []}
        location_normalizer.normalize_feature_association(fa)
        biomarker_normalizer.normalize_feature_association(fa)
        enriched_features.append(fa['features'][0])
    return enriched_features


def get_feature(args):
    """ harmonize this feature"""
    f = args['feature']
    if 'description' not in f:
        f['description'] = ''
    fa = {'features': [f], 'dev_tags': []}
    location_normalizer.normalize_feature_association(fa)
    biomarker_normalizer.normalize_feature_association(fa)
    return fa['features'][0]


def allele_identifier(feature):
    """ return the hg37 g. hgvs notation
    - or if unavailable, the gene/start/biomarker string """
    is_HG37 = re.compile('NC_.*\.10:g')
    for s in feature.get('synonyms', []):
        if is_HG37.match(s):
            return '{} {}'.format(feature['geneSymbol'], s)
    return '{} {} {}'.format(feature['geneSymbol'], feature['start'],
                             feature['sequence_ontology']['name'])


def biomarker_type(feature_associations):
    """ get the SO:name """
    for fa in feature_associations:
        for f in fa['features']:
            return f['sequence_ontology']['name']


def raw_dataframe(query_string, client, size=1000, verbose=False,
                  index='associations'):
        '''
        Get a data frame with relevant information for analysis.
        By default this excludes trials and limited to evidence with fully normalized features, environment and phenotype
        :query_string -- ES query string, defaults to only features with genomic location, no trials
        :size -- number of documents to fetch per scan
        :verbose -- print the query
        '''  # NOQA

        s = Search(using=client, index=index)
        s = s.params(size=size)
        s = s.query("query_string", query=query_string)
        if verbose:
            print json.dumps(s.to_dict(), indent=2, separators=(',', ': '))

        def hit_with_id(hit):
            '''include the unique id with the source data'''
            h = hit.to_dict()
            h['evidence.id'] = hit.meta.id
            return h

        # create df with the first level of json formatted by pandas
        # return json_normalize([hit_with_id(hit) for hit in s.scan()])
        for hit in s.scan():
            yield hit_with_id(hit)


def get_associations(args, client):
    queries = []
    enriched_features = get_features(args)

    for f in enriched_features:
        location_query = location_query_generator.generate([f])
        identifier = allele_identifier(
            location_query['feature_associations'][0]['features'][0]
        )
        b_type = biomarker_type(location_query['feature_associations'])
        for name in location_query['queries'].keys():
            q = location_query['queries'][name]
            qs = q['query']['query_string']['query']
            hits = list(raw_dataframe(query_string=qs, client=client))
            queries.append({'biomarker_type': b_type,
                            'allele': identifier,
                            'name': name,
                            'hits': hits,
                            'query_string': qs,
                            'feature': f
                            })

    counter = Counter()
    for f in enriched_features:
        for p in f.get('pathways', []):
            counter[p] += 1
    top3_pathways = [t[0] for t in counter.most_common(3)]
    log.info(('top3_pathways', top3_pathways))
    if len(top3_pathways) > 0:
        smmart_drugs = "+association.environmentalContexts.id:('CID23725625', 'CID56842121', u'CHEMBL3137343', 'CID5330286', 'CID444795', 'CID10184653', 'CID5311', 'CID6442177', 'CID11707110', 'CID25102847', 'CID9823820', 'CID24826799', u'CHEMBL1789844', u'CHEMBL2108738', u'CHEMBL2007641', u'CHEMBL1351', 'CID15951529', 'CID132971', 'CID42611257', 'CID9854073', 'CID6918837', 'CID5291', 'CID3062316', 'CID5329102', 'CID216239', 'CID25126798', 'CID387447', 'CID11625818', 'CID49846579', 'CID5284616', u'CHEMBL1201583', 'CID176870', 'CID2662')"
        sources = "-source:*trials"
        qs = '+features.pathways:({})'.format(
            ' AND '.join(['"{}"'.format(d) for d in top3_pathways]))
        hits = list(raw_dataframe(query_string=qs, client=client))
        queries.append({'biomarker_type': 'Uncategorized',
                        'allele': 'All features',
                        'name': 'pathways',
                        'hits': hits,
                        'query_string': '{} {} {}'.format(sources, smmart_drugs, qs),
                        'feature': {'pathways': top3_pathways}
                        })

    return queries
