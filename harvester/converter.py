# convert normalize data to ga4gh features and associations

from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import json
import copy

es = Elasticsearch(
    ['10.96.11.130']
)


def delete_index():
    # delete index
    try:
        indices_client = IndicesClient(es)
        indices_client.delete(index='associations')
    except Exception as e:
        pass


def delete(source):
    try:
        query = {
          "query": {
            "query_string": {
              "analyze_wildcard": True,
              "query": "source:{}".format(source)
            }
          }
        }
        es.delete_by_query(index='associations', body=query)
    except Exception as e:
        print e, query
        pass


def civic():
    civic = es.search(index='genes', doc_type='civic')
    for gene in civic['hits']['hits']:
        variants = []
        keys = []
        if 'civic' in gene['_source'] and 'variants' in gene['_source']['civic']:
            variants = gene['_source']['civic']['variants']
            for variant in variants:
                feature = {}
                feature['geneSymbol'] = variant['entrez_name']
                feature['entrez_id'] = variant['entrez_id']
                feature['start'] = variant['coordinates']['start']
                feature['end'] = variant['coordinates']['stop']
                feature['referenceName'] = variant['coordinates']['reference_build']  # NOQA
                feature['chromosome'] = variant['coordinates']['chromosome']
                feature['name'] = variant['name']
                for evidence_item in variant['evidence_items']:
                    association = {}
                    association['description'] = evidence_item['description']
                    association['environmentalContexts'] = []
                    environmentalContexts = association['environmentalContexts']
                    for drug in evidence_item['drugs']:
                        environmentalContexts.append({
                            'description': drug['name'],
                            'pubchem_id': drug['pubchem_id']
                        })
                    association['phenotype'] = {
                        'description': evidence_item['disease']['name'],
                        'id': evidence_item['disease']['url']
                    }
                    association['evidence'] = [{
                        "evidenceType": {
                            "sourceName": "CIVIC",
                            "id": '{}'.format(evidence_item['id'])
                        },
                        'description': evidence_item['clinical_significance'],
                        'info': {
                            'publications': [
                                evidence_item['source']['source_url']
                            ]
                        }
                    }],
                    # add summary fields for Display
                    association['evidence_label'] = evidence_item['clinical_significance'],
                    association['publication_url'] = evidence_item['source']['source_url'],
                    association['drug_labels'] = ','.join([drug['name'] for drug in evidence_item['drugs']])
                    # create snapshot of original data
                    v = copy.deepcopy(variant)
                    del v['evidence_items']
                    v['evidence_items'] = [evidence_item]
                    feature_association = {'gene': gene['_id'],
                                           'feature': feature,
                                           'association': association,
                                           'source':'civic',
                                           'civic': v}
                    result = es.index(index='associations',
                                      body=feature_association,
                                      id='civic-{}'.format(evidence_item['id']),
                                      doc_type='association',
                                      op_type='index')
                    if result['_shards']['failed'] > 0:
                        print 'failure updating association {}' \
                              .format(gene_feature['gene'])

def jax():
    result = es.search(index='genes3', doc_type='jax')
    for hit in result['hits']['hits']:
        gene = hit['_source']['gene']
        jax = hit['_source']['jax']
        evidence = jax['evidence']
        print gene, jax['evidence'].keys()
        # [u'approval_status', u'evidence_type', u'indication_tumor_type',
        #  u'references', u'response_type',
        #  u'therapy_name', u'molecular_profile', u'efficacy_evidence']
        feature = {}
        feature['geneSymbol'] = gene
        feature['name'] = evidence['molecular_profile']

        association = {}
        association['description'] = evidence['efficacy_evidence']
        association['environmentalContexts'] = []
        association['environmentalContexts'].append({
            'description': evidence['therapy_name']})
        association['phenotype'] = {
            'description': evidence['indication_tumor_type']
        }
        association['evidence'] = [{
            "evidenceType": {
                "sourceName": "jax"
            },
            'description': evidence['response_type'],
            'info': {
                'publications': [
                    ['http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(r) for r in evidence['references']]
                ]
            }
        }]
        # add summary fields for Display
        association['evidence_label'] = evidence['response_type']
        if len(evidence['references']) > 0:
            association['publication_url'] = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(evidence['references'][0])
        association['drug_labels'] = evidence['therapy_name']
        feature_association = {'gene': gene ,
                               'feature': feature,
                               'association': association,
                               'source': 'jax',
                               'jax': jax }
        result = es.index(index='associations',
                          body=feature_association,
                          doc_type='association',
                          op_type='index')
        if result['_shards']['failed'] > 0:
            print 'failure updating association {}' \
                  .format(gene)




def oncokb():
    result = es.search(index='genes', doc_type='oncokb')
    for hit in result['hits']['hits']:
        gene = hit['_source']['gene']
        oncokb = {'clinical': []}
        if 'oncokb' in hit['_source']:
            oncokb = hit['_source']['oncokb']
        # print hit
        # print oncokb
        # print oncokb['clinical']
        for clinical in oncokb['clinical']:
            variant = clinical['variant']
            gene_data = variant['gene']
            feature = {}
            feature['geneSymbol'] = gene
            feature['name'] = variant['name']
            feature['entrez_id'] = gene_data['entrezGeneId']

            association = {}
            association['description'] = clinical['level']
            association['environmentalContexts'] = []
            for drug in clinical['drug']:
                association['environmentalContexts'].append({'description': drug})
            association['phenotype'] = {
                'description': clinical['cancerType']['mainType']['name'],
                'id': clinical['cancerType']['mainType']['id']
            }
            association['evidence'] = [{
                "evidenceType": {
                    "sourceName": "oncokb",
                    "id": '{}-{}'.format(gene,
                                         clinical['cancerType']['mainType']['id'])
                },
                'description': clinical['level_label'],
                'info': {
                    'publications': [
                        [drugAbstracts['link'] for drugAbstracts in clinical['drugAbstracts']]
                    ]
                }
            }]
            # add summary fields for Display
            association['evidence_label'] = clinical['level_label']
            if len(clinical['drugAbstracts']) > 0:
                association['publication_url'] = clinical['drugAbstracts'][0]['link']
            else:
                for drugPmid in clinical['drugPmids']:
                    association['publication_url'] = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(drugPmid)
                    break

            association['drug_labels'] = ','.join([drug for drug in clinical['drug']])
            feature_association = {'gene': gene ,
                                   'feature': feature,
                                   'association': association,
                                   'source': 'oncokb',
                                   'oncokb': {'clinical': clinical} }
            result = es.index(index='associations',
                              body=feature_association,
                              doc_type='association',
                              op_type='index')
            if result['_shards']['failed'] > 0:
                print 'failure updating association {}' \
                      .format(gene_feature['gene'])


# #################
def ga4gh():
    ga4gh = es.search(index='genes', doc_type='ga4gh')
    for gene in ga4gh['hits']['hits']:
        ga4gh = gene['_source']['ga4gh']
        if 'features' in ga4gh:
            # print gene['gene'], len(gene['features'][0]['associations']), len(gene['features'])
            for f in ga4gh['features']:
                print f.keys()
                associations = f['associations']
                del f['associations']
                for a in associations:
                    # add summary fields for Display
                    a['evidence_label'] = a['evidence'][0]['description']
                    url = None
                    for e in a['evidence']:
                        for p in e['info']['publications']:
                            url = p
                            break
                    drugs = []
                    for e in a['environmentalContexts']:
                        drugs.append(e['description'])
                    a['publication_url'] = p
                    a['drug_labels'] = ','.join(drugs)

                    feature_association = {'gene': gene['_source']['gene'],
                                           'feature': f,
                                           'association': a,
                                           'source':'ga4gh'}
                    # print json.dumps(feature_association)
                    # print feature_association['association']['evidence'][0].keys()
                    # print feature_association['association']['evidence'][0]['evidenceType']
                    result = es.index(index='associations',
                                      body=feature_association,
                                      id='ga4gh-{}'.format(f['id']),
                                      doc_type='association',
                                      op_type='index')
                    if result['_shards']['failed'] > 0:
                        print 'failure updating association {}' \
                              .format(gene['_source']['gene'])

        # else:
        #     print gene['gene']

if __name__ == "__main__":
    #delete('civic')
    jax()
