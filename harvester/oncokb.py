#!/usr/bin/python

import requests
import json
from urllib import urlencode, quote_plus

import cosmic_lookup_table

import evidence_label as el
import evidence_direction as ed
import mutation_type as mut
from feature_enricher import enrich

LOOKUP_TABLE = None


def harvest(genes):
    i = 0
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
        clin_url = 'http://oncokb.org/api/private/search/variants/clinical?hugoSymbol={}'  # NOQA
        clin_url = clin_url.format(gene)
        clin_r = requests.get(clin_url)
        if clin_r.status_code != 200:
            print "{} {} {}".format(gene, clin_url, clin_r.status_code)
        else:
            gene_data['oncokb']['clinical'] = clin_r.json()
            for clinical in gene_data['oncokb']['clinical']:
                key = "LEVEL_{}".format(clinical['level'])
                if key in levels:
                    clinical['level_label'] = levels[key]
                else:
                    print '{} not found'.format(clinical['level'])
        clin_r.close()
        bio_url = 'http://oncokb.org/api/private/search/variants/biological?hugoSymbol={}'  # NOQA
        bio_url = bio_url.format(gene)
        bio_r = requests.get(bio_url)
        if bio_r.status_code != 200:
            print "{} {} {}".format(gene, bio_url, bio_r.status_code)
        else:
            print i
            i = i + len(bio_r.json())
            gene_data['oncokb']['biological'] = bio_r.json()
            for biological in gene_data['oncokb']['biological']:
                biological['level_label'] = 'NA'
        bio_r.close()
        print i
        yield gene_data


def convert(gene_data):
    global LOOKUP_TABLE
    gene = gene_data['gene']
    oncokb = {'clinical': [], 'biological': []}

    def _enrich_feature(gene, feature):
        global LOOKUP_TABLE
        # Look up variant and add position information.
        if not LOOKUP_TABLE:
            LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                    "./cosmic_lookup_table.tsv")
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
        else:
            feature = enrich(feature)
        return feature

    if 'oncokb' in gene_data:
        oncokb = gene_data['oncokb']
    # this section yields a feature association for the predictive evidence
    for clinical in oncokb['clinical']:
        variant = clinical['variant']
        alteration = variant['alteration']
        gene_data = variant['gene']

        # if feature is 'Oncogenic Mutations' then merge in biological
        features = []
        if variant['name'] == 'Oncogenic Mutations':
            for biological in oncokb['biological']:
                if biological['oncogenic'] in ['Likely Oncogenic', 'Oncogenic']:
                    variant = biological['variant']
                    gene_data = variant['gene']
                    alteration = variant['alteration']
                    feature = {}
                    feature['geneSymbol'] = gene
                    feature['description'] = variant['name']
                    feature['name'] = variant['name']
                    feature['entrez_id'] = gene_data['entrezGeneId']
                    feature['biomarker_type'] = mut.norm_biomarker(
                        variant['consequence']['term'])
                    feature = _enrich_feature(gene, feature)
                    features.append(feature)
        else:
            feature = {}
            feature['geneSymbol'] = gene
            feature['name'] = variant['name']
            feature['description'] = variant['name']
            feature['entrez_id'] = gene_data['entrezGeneId']
            feature['biomarker_type'] = mut.norm_biomarker(
                variant['consequence']['term'])
            feature = _enrich_feature(gene, feature)
            features.append(feature)

        association = {}
        association['description'] = clinical['level_label']
        association['variant_name'] = variant['name']
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
                'publications':
                    [drugAbstracts['link']
                        for drugAbstracts in clinical['drugAbstracts']]
            }
        }]
        # add summary fields for Display
        association['source_link'] = 'http://oncokb.org/#/gene/{}/variant/{}'.format(gene,
                                     quote_plus(variant['name']))
        association = el.evidence_label(clinical['level'],
                                        association, na=True)
        association = ed.evidence_direction(clinical['level_label'],
                                            association, na=True)

        if len(clinical['drugAbstracts']) > 0:
            association['publication_url'] = clinical['drugAbstracts'][0]['link']  # NOQA
        else:
            for drugPmid in clinical['drugPmids']:
                association['publication_url'] = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(drugPmid)  # NOQA
                break

        association['drug_labels'] = ','.join([drug for drug in clinical['drug']])   # NOQA
        feature_names = ', '.join(['{}:{}'.format(
                                f["geneSymbol"], f["name"]) for f in features])
        feature_association = {'genes': [gene],
                               'features': features,
                               'feature_names': feature_names,
                               'association': association,
                               'source': 'oncokb',
                               'oncokb': {'clinical': clinical}}
        yield feature_association

    # this section yields a feature association for the oncogenic evidence
    for biological in oncokb['biological']:
        variant = biological['variant']
        gene_data = variant['gene']
        alteration = variant['alteration']

        feature = {}
        feature['geneSymbol'] = gene
        feature['name'] = variant['name']
        feature['entrez_id'] = gene_data['entrezGeneId']
        feature['biomarker_type'] = mut.norm_biomarker(
            variant['consequence']['term'])

        # Look up variant and add position information.
        if not LOOKUP_TABLE:
            LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                    "./cosmic_lookup_table.tsv")
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
        association['variant_name'] = variant['name']
        association['description'] = variant['consequence']['description']
        association['environmentalContexts'] = []

        if biological['oncogenic'] in ['Likely Oncogenic', 'Oncogenic']:
            association['phenotype'] = {
                'description': 'cancer'
            }

        association['evidence'] = [{
            "evidenceType": {
                "sourceName": "oncokb",
                "id": '{}-{}'.format(gene,
                                     biological['oncogenic'])
            },
            'description': biological['mutationEffect'],
            'info': {
                'publications':
                    ['http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(Pmid)
                        for Pmid in biological['mutationEffectPmids']]
            }
        }]
        # add summary fields for Display
        # print variant['name']
        # print variant['name'].__class__
        # print gene
        # print gene.__class__
        #
        # association['source_link'] = \
        #     'http://oncokb.org/#/gene/{}/variant/{}' \
        #     .format(gene, urlencode(str(variant['name'])))

        association['oncogenic'] = biological['oncogenic']
        association['evidence_label'] = None
        association = ed.evidence_direction(biological['level_label'],
                                            association, na=True)

        if len(biological['mutationEffectPmids']) > 0:
            for drugPmid in biological['mutationEffectPmids']:
                association['publication_url'] = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(drugPmid)  # NOQA
                break

        feature_names = feature["geneSymbol"] + ' ' + feature["name"]
        feature_association = {'genes': [gene],
                               'features': [feature],
                               'feature_names': feature_names,
                               'association': association,
                               'source': 'oncokb',
                               'oncokb': {'biological': biological}}
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
