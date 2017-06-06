#!/usr/bin/python

import requests
import json

import cosmic_lookup_table

LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup("./cosmic_lookup_table.tsv")

import evidence_label as el
import evidence_direction as ed 

def harvest(genes):
    r = requests.get('http://oncokb.org/api/v1/levels')
    levels = r.json()
    if not genes:
        r = requests.get('http://oncokb.org/api/v1/genes')
        all_genes = r.json()
        genes = []
        for gene in all_genes:
            genes.append(gene['hugoSymbol'])
    for gene in set(genes):
        gene_data = {'gene': gene, 'oncokb': {}}
        url = 'http://oncokb.org/api/private/search/variants/clinical?hugoSymbol={}'  # NOQA
        url = url.format(gene)
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
        r.close()
        yield gene_data


def convert(gene_data):
    gene = gene_data['gene']
    oncokb = {'clinical': []}
    if 'oncokb' in gene_data:
        oncokb = gene_data['oncokb']
    for clinical in oncokb['clinical']:
        variant = clinical['variant']
        alteration = variant['alteration']
        gene_data = variant['gene']
        feature = {}
        feature['geneSymbol'] = gene
        feature['name'] = variant['name']
        feature['entrez_id'] = gene_data['entrezGeneId']

        # Look up variant and add position information.
        matches = LOOKUP_TABLE.get_entries(gene, alteration)
        if len(matches) > 0:
            # FIXME: just using the first match for now;
            # it's not clear what to do if there are multiple matches.
            match = matches[0]
            feature['chromosome'] = str(match['chrom'])
            feature['start'] = match['start']
            feature['end'] = match['end']
            feature['ref'] = match['ref']
            feature['alt'] = match['alt']
            feature['referenceName'] = str(match['build'])

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
            'description': clinical['level'],
            'info': {
                'publications': [
                    [drugAbstracts['link'] for drugAbstracts in clinical['drugAbstracts']]
                ]
            }
        }]
        # add summary fields for Display
        association['evidence_label'] = clinical['level_label']
        
        for item in el.ev_lab:
            for opt in el.ev_lab[item]:
                if opt in clinical['level_label'].lower():
                    association['evidence_label'] = item
        if 'evidence_label' not in association:
            association['evidence_label'] = 'NA'

        for item in ed.res_type:
            for opt in ed.res_type[item]:
                if opt in clinical['level_label'].lower():
                    association['response_type'] = item
        if 'response_type' not in association:
            association['response_type'] = 'NA'

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


def _test():
    for feature_association in harvest_and_convert(None):
        print feature_association.keys()
        break

if __name__ == '__main__':
    _test()
