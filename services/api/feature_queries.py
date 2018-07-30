import logging
import requests_cache
import re
from harvester import location_normalizer, biomarker_normalizer
from elasticsearch_dsl import Search, Q

from collections import Counter
import os

DATA_DIR = os.environ.get('HARVESTER_DATA', '../data')

# cache responses
requests_cache.install_cache('{}/harvester'.format(DATA_DIR),
                             allowable_codes=(200, 400, 404))
# our logger
log = logging.getLogger(__name__)

SMMART_DRUGS = '+association.environmentalContexts.id:("CID23725625","CID56842121","CHEMBL3137343","CID5330286","CID444795","CID10184653","CID5311","CID6442177","CID11707110","CID25102847","CID9823820","CID24826799","CHEMBL1789844","CHEMBL2108738","CHEMBL2007641","CHEMBL1351","CID15951529","CID132971","CID42611257","CID9854073","CID6918837","CID5291","CID3062316","CID5329102","CID216239","CID25126798","CID387447","CID11625818","CID49846579","CID5284616","CHEMBL1201583","CID176870","CID2662")'  # noqa


def get_features(args):
    """ harmonize these features"""
    enriched_features = []
    for f in args['features']:
        fa = {'features': [f], 'dev_tags': []}
        # location_normalizer.normalize_feature_association(fa)
        # biomarker_normalizer.normalize_feature_association(fa)
        enriched_features.append(fa['features'][0])
    return enriched_features


def get_feature(args):
    """ harmonize this feature"""
    f = args['feature']
    if 'description' not in f:
        f['description'] = ''
    fa = {'features': [f], 'dev_tags': []}
    # location_normalizer.normalize_feature_association(fa)
    # biomarker_normalizer.normalize_feature_association(fa)
    return fa['features'][0]


def allele_identifier(feature):
    """ return the hg37 g. hgvs notation
    - or if unavailable, the gene/start/biomarker string """
    is_HG37 = re.compile('NC_.*\.10:g')
    for s in feature.get('synonyms', []):
        if is_HG37.match(s):
            return '{} {}'.format(feature['geneSymbol'], s)
    return '{} {} {}'.format(feature['geneSymbol'], feature['start'],
                             feature.get('sequence_ontology', {'name': ''} )['name'])


def biomarker_type(feature):
    """ get the SO:name """
    return feature.get('sequence_ontology', {'name': ''} )['name']


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


def to_elastic(queries, user_query=None, all_drugs=False, smmart_drugs=None, all_sources=False,
               sources=None):
    if not all_drugs and not smmart_drugs:
        smmart_drugs = SMMART_DRUGS  # noqa
    if not all_sources and not sources:
        sources = "-source:*trials"
    for query, name in queries:
        if user_query:
            query = '{} {}'.format(user_query, query)
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


def generate(features, user_query):
    def make_queries(features, user_query):
        # +features.protein_effects:()
        protein_effects = []
        genes = []
        genomic_locations = []
        genomic_starts = []
        genomic_ranges = []
        protein_domains = []
        pathways = []
        biomarker_types = []
        for f in features:

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
                genomic_starts.append({'chromosome': f['chromosome'], 'range': [str(f['start']-i) for i in range(-2, 3)]})  # noqa
		if 'end' in f:
                    genomic_ranges.append({'chromosome': f['chromosome'], 'start': f['start'], 'end': f['end']})  # noqa
		else:
		    genomic_ranges.append({'chromosome': f['chromosome'], 'start': f['start']}) # noqa

            for protein_domain in f.get('protein_domains', []):
                # do not include these domains
                if protein_domain['name'] in [1, 2, 3, 4]:
                    continue
                protein_domains.append(protein_domain['name'])

            for pathway in f.get('pathways', []):
                pathways.append(pathway)

            if 'sequence_ontology' in f:
                biomarker_types.append((f['geneSymbol'],
                                        f['sequence_ontology']['name']))

            genes.append(f['geneSymbol'])

        protein_effects = list(set(protein_effects))
        genes = list(set(genes))
        genomic_locations = list(set(genomic_locations))
        protein_domains = list(set(protein_domains))
        pathways = list(set(pathways))
        biomarker_types = list(set(biomarker_types))

        if len(protein_effects) > 0:
            yield '+features.protein_effects:({})'.format(' OR '.join(protein_effects)), 'protein_effects'  # noqa
        yield '+genes:({})'.format(' OR '.join(genes)), 'genes'
        if len(genomic_locations) > 0:
            yield '+features.synonyms:({})'.format(' OR '.join(['"{}"'.format(g) for g in genomic_locations])), 'alleles'  # noqa
        if len(protein_domains) > 0:
            yield '+features.protein_domains.name:({})'.format(' OR '.join(["'{}'".format(d) for d in protein_domains])), 'protein_domains'  # noqa

        chromosome_starts = []
        for genomic_start in genomic_starts:
            chromosome_starts.append('+features.chromosome:{} +features.start:({})'.format(genomic_start['chromosome'], ' OR '.join(genomic_start['range'])))  # noqa
        yield ' OR '.join(chromosome_starts), '~location'

        chromosome_ranges = []
        for genomic_range in genomic_ranges:
            chromosome_ranges.append('+features.chromosome:{} +features.start:>={} +features.end:<={}'.format(genomic_range['chromosome'], genomic_range['start'], genomic_range['end']))  # noqa
        yield ' OR '.join(chromosome_ranges), '~range'

        biomarker_queries = []
        for t in biomarker_types:
            biomarker_queries.append('+features.geneSymbol:{} +features.sequence_ontology.name:{}'.format(t[0], t[1]))  # noqa
        if len(biomarker_queries) > 0:
            yield ' OR '.join(biomarker_queries),  '~biomarker_type'

    response = {'queries': {}, 'features': features}
    for q in to_elastic(make_queries(features, user_query), user_query):
        response['queries'][q['name']] = q['query']
    return response


def get_associations(args, client):
    queries = []
    enriched_features = get_features(args)
    user_query = args.get('q', '')
    for f in enriched_features:
        location_query = generate([f], user_query)
        identifier = allele_identifier(f)
        b_type = biomarker_type(f)
        for name in location_query['queries'].keys():
            q = location_query['queries'][name]
            qs = q['query']['query_string']['query']
            hits = list(raw_dataframe(query_string=qs, client=client))
            queries.append({'biomarker_type': b_type,
                            'allele': identifier,
                            'name': name,
                            'hits': hits,
                            'query_string': '{} {}'.format(qs, user_query) ,
                            'feature': f
                            })

    counter = Counter()
    for f in enriched_features:
        for p in f.get('pathways', []):
            counter[p] += 1
    top3_pathways = [t[0] for t in counter.most_common(3)]
    log.info(('top3_pathways', top3_pathways))
    if len(top3_pathways) > 0:
        sources = "-source:*trials"
        qs = '+features.pathways:({})'.format(
            ' AND '.join(['"{}"'.format(d) for d in top3_pathways]))
        hits = list(raw_dataframe(query_string=qs, client=client))
        queries.append({'biomarker_type': 'Uncategorized',
                        'allele': 'All features',
                        'name': 'pathways',
                        'hits': hits,
                        'query_string': '{} {} {} {}'.format(sources, SMMART_DRUGS, qs, user_query),  # noqa
                        'feature': {'pathways': top3_pathways}
                        })

    return queries
