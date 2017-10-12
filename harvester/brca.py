#!/usr/bin/python

import requests
import copy
import evidence_label as el
import evidence_direction as ed
import mutation_type as mut
import sys
import logging


def harvest(genes=None):
    """ there is only one gene, BRCA, ignore passed parameter"""
    # harvest all genes
    page_num = 0
    more_data = True
    while more_data:
        r = requests.get('http://brcaexchange.org/backend/data/?format=json&order_by=Gene_Symbol&direction=ascending&page_size=100&page_num={}&search_term=&include=Variant_in_ENIGMA&include=Variant_in_ClinVar&include=Variant_in_1000_Genomes&include=Variant_in_ExAC&include=Variant_in_LOVD&include=Variant_in_BIC&include=Variant_in_ESP&include=Variant_in_exLOVD'.format(page_num))  # NOQA
        payload = r.json()
        if ('data' not in payload or len(payload['data']) == 0):
            more_data = False
        else:
            page_num = page_num + 1
            for record in payload['data']:
                if not record['Pathogenicity_expert'] == 'Not Yet Reviewed':
                    gene = record['Gene_Symbol']
                    gene_data = {'gene': gene, 'brca': record}
                    yield gene_data


def convert(gene_data):
    """ given gene data from brca, convert it to ga4gh """
    try:
        brca = gene_data['brca']
        feature = {}
        feature['geneSymbol'] = brca['Gene_Symbol']
        # feature['entrez_id'] = ?
        builds = ['Hg38', 'Hg37', 'Hg36']
        for build in builds:
            if '{}_Start'.format(build) in brca:
                feature['start'] = brca['{}_Start'.format(build)]
                feature['end'] = brca['{}_End'.format(build)]
                feature['referenceName'] = build
                break

        feature['chromosome'] = str(brca['Chr'])
        feature['ref'] = brca['Ref']
        feature['alt'] = brca['Alt']
        feature['name'] = brca['Protein_Change']
        if len(feature['name']) == 0:
            feature['name'] = brca['HGVS_cDNA']
        # feature['biomarker_type'] = ?
        association = {}
        association['description'] = brca['Pathogenicity_expert']
        association['environmentalContexts'] = []
        association['phenotype'] = {
            'description': brca['Condition_ID_value_ENIGMA'],
            # 'id': ?
        }

        citations = brca['Clinical_significance_citations_ENIGMA']
        info = None
        if not citations == '-':
            pubmed = "http://www.ncbi.nlm.nih.gov/pubmed/{}".format(citations.split(':')[1])
            info = {'publications': [pubmed]}

        association['evidence'] = [{
            "evidenceType": {
                "sourceName": "brca",
                "id": '{}'.format(brca['id'])
            },
            'description': brca['Clinical_Significance_ClinVar'],
            'info': info
        }]
        # add summary fields for Display
        association['oncogenic'] = brca['Clinical_Significance_ClinVar'].split(',')[0]
        association['evidence_label'] = None
        feature_association = {'genes': [brca['Gene_Symbol']],
                               'features': [feature],
                               'feature_names': [feature['name']],
                               'association': association,
                               'source': 'brca',
                               'brca': brca}
        yield feature_association

    except Exception as e:
        logging.error(gene_data['gene'], exc_info=1)


def harvest_and_convert(genes):
    """ get data from brca, convert it to ga4gh and return via yield """
    for gene_data in harvest(genes):
        # print "harvester_yield {}".format(gene_data.keys())
        for feature_association in convert(gene_data):
            # print "convert_yield {}".format(feature_association.keys())
            yield feature_association

# main
if __name__ == '__main__':
    import yaml
    import logging.config
    path = 'logging.yml'
    with open(path) as f:
        config = yaml.load(f)
    logging.config.dictConfig(config)

    # for feature_association in harvest_and_convert(["MDM2"]):
    #     logging.info(feature_association)
    for feature_association in harvest_and_convert([]):
        logging.info(feature_association)
        exit(1)
        # logging.info(gene_data['brca']['ClinVarAccession_ENIGMA'])
