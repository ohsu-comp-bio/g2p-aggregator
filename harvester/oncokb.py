#!/usr/bin/python

import requests
import json


def harvest(genes):
    r = requests.get('http://oncokb.org/api/v1/levels')
    # if 'data' not in r.json():
    #     print r.json()
    #     exit(1)
    levels = r.json()  # ['data']
    # print levels
    for gene in set(genes):
        gene_data = {'gene': gene, 'oncokb': {}}
        url = 'http://oncokb.org/api/private/search/variants/clinical?hugoSymbol={}'
        # url = 'http://oncokb.org/public-api/v1/search/variants/clinical?hugoSymbol={}'  # NOQA
        url = url.format(gene)
        print url
        r = requests.get(url)
        if r.status_code != 200:
            print "{} {} {}".format(gene, url, r.status_code)
        else:
            gene_data['oncokb']['clinical'] = r.json()
            for clinical in gene_data['oncokb']['clinical']:
                key = "LEVEL_{}".format(clinical['level'])
                if key in levels:
                    clinical['level_label'] = levels[key]
                else:
                    print '{} not found'.format(clinical['level'])
            # print "{} Found {} clincal evidence".format(gene,  len(gene_data['oncokb']['clinical']))
        r.close()
        yield gene_data


def convert(gene_data):
    gene = gene_data['gene']
    oncokb = {'clinical': []}
    if 'oncokb' in gene_data:
        oncokb = gene_data['oncokb']
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
        association['description'] = clinical['level_label']
        association['environmentalContexts'] = []
        for drug in clinical['drug']:
            association['environmentalContexts'].append({'description': drug})
        association['phenotype'] = {
            'description': clinical['cancerType']['mainType']['name'],
            'id': '{}'.format(clinical['cancerType']['mainType']['id'])
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
                               'oncokb': {'clinical': clinical}}
        yield feature_association


def harvest_and_convert(genes):
    """ get data from oncokb, convert it to ga4gh and return via yield """
    for gene_data in harvest(genes):
        # print "harvester_yield {}".format(jax_evidence.keys())
        for feature_association in convert(gene_data):
            # print "convert_yield {}".format(feature_association.keys())
            yield feature_association


def main():
    for feature_association in harvest_and_convert(['FGFR1']):
        print feature_association.keys()

if __name__ == '__main__':
    main()
