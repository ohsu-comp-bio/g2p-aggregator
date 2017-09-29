from pyzotero.zotero import Zotero
import os
import sys
import json
import cosmic_lookup_table

LOOKUP_TABLE = None

smmart_library = 1405957
api_key = os.environ.get("ZOTERO_API_KEY")
z = Zotero(smmart_library, 'group', api_key)

def _get_cancer_collections(item_coll):
    return_coll = []
    grabbed_colls = ['aml', 'breast', 'pancreas', 'prostate']
    collections = z.collections()
    for coll in collections:
        key = coll['data']['key']
        name = coll['data']['name'].lower()
        if item_coll == key and name in grabbed_colls:
            return_coll.append(coll['data']['name'])
    return return_coll

def harvest(genes):
    """ given an array of gene symbols, harvest them from civic """
    # harvest all genes
    if not genes:
        if not LOOKUP_TABLE:
            LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                "./cosmic_lookup_table.tsv")
            genes = LOOKUP_TABLE.get_genes()

    z = Zotero(smmart_library, 'group', api_key)
    articles = z.items()
    for gene in genes:
        for art in articles:
            if gene in art['data']['extra']:
                gene_data = {'gene': gene, 'zotero': art}
                yield gene_data

def convert(gene_data):
    gene = gene_data['gene']
    if 'zotero' in gene_data:
       zotero = gene_data['zotero']
    feature = {}
    feature['geneSymbol'] = gene
    feature['name'] = ''
#    feature['biomarker_type'] = mut.norm_biomarker(
#        variant['consequence']['term'])

    association = {}
    association['description'] = zotero['data']['title']
    association['environmentalContexts'] = []
    association['drug_labels'] = []
    association['drug_labels'] = ','.join([tag['tag'] for tag in zotero['data']['tags']])
    for drug in association['drug_labels']:
        association['environmentalContexts'].append({'description': drug})
    association['phenotype'] = {
        'description' : _get_cancer_collections(zotero['data']['collections'])
    }
    association['evidence'] = [{
        "evidenceType": {
            "sourceName": "zotero",
            "id": '{}-{}'.format(gene, association['phenotype']['description'])
        },
        'description': '',
        'info': {
            'publications': zotero['data']['url']['link']
        }
    }]
    association = el.evidence_label(association, na=True)
    association = ed.evidence_direction(association, na=True)
    association['publication_url'] = zotero['data']['url']['link']
    feature_names = feature["geneSymbol"] + ' ' + feature["name"]
    feature_association = {'genes': [gene],
                           'features': [feature],
                           'feature_names': feature_names,
                           'association': association,
                           'source': 'zotero',
                           'zotero': zotero}
    yield feature_association

def harvest_and_convert(genes):
    """ get article data from zotero, convert to g2p format """
    for gene_data in harvest(genes):
        for feature_association in convert(gene_data):
            yield feature_association

def _test():
    for feature_association in harvest_and_convert(None):
        print feature_association.keys()
        break

if __name__ == '__main__':
    _test()
