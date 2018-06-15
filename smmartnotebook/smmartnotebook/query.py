# so we can call the g2p service
import requests
import json

# for processing results
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import traceback


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



def query(url, features, verify=True, timeout=60*5):
    """ query the /api/v1/features/associations endpoint
        returns a tuple of (queries, data_frames, summary)
    """
    query_weights = {
        'alleles': 100,
        '~location': 90,
        '~range': 50,
        'protein_effects': 40,
        'protein_domains': 30,
        '~biomarker_type': 20,
        'genes': 10,
        'pathways': 0
    }

    queries = []
    data_frames = {}
    t = datetime.datetime.now()

    rsp = requests.post(url, json=features, verify=verify, timeout=timeout)

    location_queries = rsp.json()

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
        queries_summary[q['allele']]['hits-{}'.format(q['name'])] = q['hits']
        queries_summary[q['allele']]['weighted_hits'] = q['hits'] * query_weights.get(name, 0)

    summary = pd.DataFrame.from_records([queries_summary[k]
                                        for k in queries_summary.keys()])
    summary = summary.fillna(0)

    return queries, data_frames, summary
