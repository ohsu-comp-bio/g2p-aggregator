
# so we can call the g2p service
import requests
import json

# for processing results
import pandas as pd
import numpy as np
from collections import Counter
import datetime


def to_df(generator, feature):
    """ some client side utility code to take the query results and
        xform into data frame """
    def to_dict(generator, feature):
        for hit in generator:
            drugs = [ec.get('term', ec['description'])
                     .encode('utf-8')
                     for ec in hit['association']['environmentalContexts']]
            description = hit['association']['description'].encode('utf-8')
            source = hit['source'].encode('utf-8')
            evidence_label = hit['association']['evidence_label']
            id = hit['evidence.id']
            phenotype = hit['association']['phenotype']['type']['term']\
                .encode('utf-8')
            publications = []
            matches = []

            try:
                # compare the queried feature vs all the features in the hit.
                # highlight the matches
                f = feature
                if f:
                    for f2 in hit.get('features', []):
                        if not f2:
                            continue
                        for s in f.get('synonyms', []):
                            if s in f2.get('synonyms', []):
                                matches.append(s)
                        for p in f.get('pathways', []):
                            if p in f2.get('pathways', []):
                                matches.append('pathway')
                        for sp in f.get('swissprots', []):
                            if sp in f2.get('swissprots', []):
                                matches.append(sp)

                        if f.get('sequence_ontology', {'name': 'X'}) == \
                                f2.get('sequence_ontology', {'name': None}):
                            matches.append(f['sequence_ontology']['name'])

                        if f.get('geneSymbol', None) == f2.get('geneSymbol',
                                                               None):
                            matches.append(f.get('geneSymbol', None))

                matches = list(set(matches))

                for e in hit['association']['evidence']:
                    for p in e['info']['publications']:
                        publications.append(p)

                yield {'id': id,
                       'source': source,
                       'evidence_label': evidence_label,
                       'drugs': drugs,
                       'description': description,
                       'phenotype': phenotype,
                       'publications': publications,
                       'matches': matches
                       }
            except Exception as e:
                print '!!!', e

    try:
        return pd.DataFrame.from_records(to_dict(generator, feature),
                                         index='id')
    except Exception as e:
        # might be empty
        return pd.DataFrame()


def query(url, features, verify=True):
    """ query the /api/v1/features/associations endpoint
        returns a tuple of (queries, data_frames, summary)
    """
    queries = []
    data_frames = {}
    t = datetime.datetime.now()

    rsp = requests.post(url, json=features, verify=verify)

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
        # lets recast the hits to a hit count
        evidence_ids.extend([hit['evidence.id']
                            for hit in location_query['hits']])
        location_query['hits'] = len(location_query['hits'])
        queries.append(location_query)

    print '{} queries, {} total hits, {} unique hits returned in {}'.format(
        len(queries),
        len(evidence_ids),
        len(list(set(evidence_ids))),
        datetime.datetime.now() - t)

    queries_summary = {}
    for q in queries:
        if q['allele'] not in queries_summary:
            queries_summary[q['allele']] = {
                'allele': q['allele'], 'biomarker_type': q['biomarker_type']}
        queries_summary[q['allele']]['hits-{}'.format(q['name'])] = q['hits']

    summary = pd.DataFrame.from_records([queries_summary[k]
                                        for k in queries_summary.keys()])
    summary = summary.fillna(0)

    return queries, data_frames, summary
