import logging
import requests_cache
import re
from harvester import location_normalizer, location_query_generator, \
    biomarker_normalizer
from elasticsearch_dsl import Search, Q

from collections import Counter

# cache responses
requests_cache.install_cache('harvester', allowable_codes=(200, 400, 404))
# our logger
log = logging.getLogger(__name__)


def get_features(args):
    """ find all associations associated with these features"""
    enriched_features = []
    for f in args['features']:
        fa = {'features': [f], 'dev_tags': []}
        location_normalizer.normalize_feature_association(fa)
        biomarker_normalizer.normalize_feature_association(fa)
        enriched_features.append(fa['features'][0])
    return enriched_features


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
        qs = '+features.pathways:({})'.format(
            ' AND '.join(['"{}"'.format(d) for d in top3_pathways]))
        hits = list(raw_dataframe(query_string=qs, client=client))
        queries.append({'biomarker_type': None,
                        'allele': 'All features',
                        'name': 'pathways',
                        'hits': hits,
                        'query_string': qs,
                        'feature': None
                        })

    return queries
