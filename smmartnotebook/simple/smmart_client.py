# so we can call the g2p service
import requests
import json

# for processing results
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import traceback

# for reading MAF files
import csv
import concurrent.futures

DEFAULT_URL = 'https://dms-dev.compbio.ohsu.edu'

def to_df(generator, feature):
    """ some client side utility code to take the query results and
        xform into data frame """
    def to_dict(generator, feature):
        for hit in generator:
            drugs = [ec.get('term', ec['description'])
                     .encode('utf-8')
                     for ec in hit['association']['environmentalContexts']]
            drugs = b",".join(drugs).decode("utf-8") 
            description = hit['association']['description'] # .decode('utf-8')
            source = hit['source'] # .decode('utf-8')
            evidence_label = hit['association']['evidence_label']
            genes = hit['genes']
            genes = ",".join(genes)
            id = hit['evidence.id']
            phenotypes = [phenotype['term'].encode('utf-8') for phenotype in hit['association']['phenotypes']]
            phenotypes = b",".join(phenotypes).decode("utf-8") 
            publications = []
            matches = []

            try:
#                 # compare the queried feature vs all the features in the hit.
#                 # highlight the matches
#                 f = feature
#                 if f:
#                     for f2 in hit.get('features', []):
#                         if not f2:
#                             continue
#                         for s in f.get('synonyms', []):
#                             if s in f2.get('synonyms', []):
#                                 matches.append(s)
#                         for p in f.get('pathways', []):
#                             if p in f2.get('pathways', []):
#                                 matches.append('pathway')
#                         for sp in f.get('swissprots', []):
#                             if sp in f2.get('swissprots', []):
#                                 matches.append(sp)

#                         for pe in f.get('protein_effects', []):
#                             pe = pe.split(':')[1]
#                             for pe2 in f2.get('protein_effects', []):
#                                 pe2 = pe2.split(':')[1]
#                                 if pe == pe2:
#                                     matches.append(pe)

#                         for pd in f.get('protein_domains', []):
#                             for pd2 in f2.get('protein_domains', []):
#                                 if pd['name'] == pd2['name']:
#                                     matches.append(pd['name'])

#                         if f.get('sequence_ontology', {'name': 'X'}) == \
#                                 f2.get('sequence_ontology', {'name': None}):
#                             matches.append(f['sequence_ontology']['name'])

#                         if f.get('geneSymbol', None) == f2.get('geneSymbol',
#                                                                None):
#                             matches.append(f.get('geneSymbol', None))

#                 matches = list(set(matches))

                for e in hit['association']['evidence']:
                    for p in e['info']['publications']:
                        publications.append(p)
                publications = ",".join(publications)

                        
                yield {'id': id,
                       'source': source,
                       'evidence_label': evidence_label,
                       'drugs': drugs,
                       'description': description,
                       'phenotypes': phenotypes,
                       'publications': publications,
#                        'matches': matches,
                       'genes': genes
                       }
            except Exception as e:
                print('!!! {}'.format(e))
                traceback.print_exc()        

    try:
        return pd.DataFrame.from_records(to_dict(generator, feature), index='id')
    except TypeError:
        # might be empty
        return pd.DataFrame()
    except:
        raise
    


def query(features, url='https://dms-dev.compbio.ohsu.edu/api/v1/features/associations', verify=True, timeout=60*5):
    """ query the /api/v1/features/associations endpoint
        returns a tuple of (queries, data_frames, summary)
    """
    query_weights = {
        'alleles': 100,
        '~location': 90,
        '~biomarker_type': 20,
        '~range': 15,
        'genes': 10,
        'protein_effects': 1,
        'protein_domains': 1,
        'pathways': 1        
    }
    
    queries = []
    data_frames = {}
    t = datetime.datetime.now()

    rsp = requests.post(url, json=features, verify=verify, timeout=timeout)

    location_queries = None
    try:
        location_queries = rsp.json()
    except :
        print(rsp.text)
        raise

    evidence_ids = []

    for location_query in location_queries:
        allele = location_query['allele']
        name = location_query['name']
        biomarker_type = location_query['biomarker_type']
        if allele not in data_frames:
            data_frames[allele] = {}
        data_frames[allele][name] = to_df(location_query['hits'],
                                          location_query['feature'])
        # now that we have the associations in a dataframe,
        # lets recast the hits to a hit count * weight
        evidence_ids.extend([hit['evidence.id']
                            for hit in location_query['hits']])
        location_query['hits'] = len(location_query['hits'])
        queries.append(location_query)

    print('{} queries, {} total hits, {} unique hits returned in {}'.format(
        len(queries),
        len(evidence_ids),
        len(list(set(evidence_ids))),
        datetime.datetime.now() - t))

    queries_summary = {}
    for q in queries:
        if q['allele'] not in queries_summary:
            queries_summary[q['allele']] = {
                'allele': q['allele'], 'biomarker_type': q['biomarker_type'], 'weighted_hits': 0}
        queries_summary[q['allele']]['{}'.format(q['name'])] = q['hits']
        queries_summary[q['allele']]['weighted_hits'] += q['hits'] * query_weights.get(q['name'], 0)
    columns = ['allele', 'alleles','~location','~biomarker_type','~range','genes','protein_effects','protein_domains','pathways','weighted_hits']       
    summary = pd.DataFrame.from_records([queries_summary[k]
                                        for k in queries_summary.keys()], columns=columns).sort_values(by='weighted_hits', ascending=False)
    summary = summary.fillna(0)

    return queries, data_frames, summary



def maf_to_features(path):
    """ extract the features from a MAF file"""
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            # variant = 'variant:GRCh37:{}:{}:{}:{}:{}'.format(row['Chromosome'], row['Start_position'], row['End_position'], row['Reference_Allele'], row['Tumor_Seq_Allele2'])
            feature = {}
            feature['chromosome'] = row['Chromosome']
            feature['start'] = int(row['Start_Position'])
            if row['End_position']:
                feature['end'] = int(row['End_position'])
            feature['ref'] = row['Reference_Allele']
            feature['alt'] = row['Tumor_Seq_Allele2']
            feature['referenceName'] = 'GRCh37'
            feature['geneSymbol'] = row['Hugo_Symbol']
            feature['name'] = feature['description'] = ''
            if row.get('Variant_Classification', None):
                feature['biomarker_type'] = row.get('Variant_Classification', None)
#             feature['name'] = '{} {}'.format(row['Hugo_Symbol'],
#                                              row['Protein_Change'])
#             if row.get('Description', None):
#                 feature['description'] = row.get('Description')
#             else:
#                 feature['description'] = ''
#             feature['biomarker_type'] = row['Variant_Classification']
            yield feature


def fetcher(url, feature):
    """ enrich the feature """
#     start = datetime.now()
    rsp = requests.post(url, json=feature, timeout=120)
    enriched_feature = rsp.json()
#     end = datetime.now()
#     if 'name' in enriched_feature:
#         print(enriched_feature['name'], feature['chromosome'], end-start )
#     else:
#         print(feature['name'], enriched_feature)
    return enriched_feature
    

def maf_to_enriched_features(path, url='https://dms-dev.compbio.ohsu.edu/api/v1/feature'):    
    """ read a maf and return enricched features, ready for g2p """
    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        # Start the load operations and mark each future with its URL
        future_to_feature = {executor.submit(fetcher, url, feature): feature for feature in maf_to_features(path)}    
        # future_to_feature = {executor.submit(fetcher, url, feature): feature for feature in exception_features_previous}
        for future in concurrent.futures.as_completed(future_to_feature):
            feature = future_to_feature[future]
            feature_name = feature['name']
            try:
                yield future.result()
            except Exception as exc:
                print('{} generated an exception: {}'.format(feature_name, exc))
                raise 
                # exception_features.append(feature)

                
                
def maf_to_evidence(path, url=DEFAULT_URL + '/api/v1/features/associations'):    
    features = [f for f in maf_to_features(path)]
    return query(features, url)