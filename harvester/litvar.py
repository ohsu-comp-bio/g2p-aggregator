import requests
import json
import logging
import httplib as http_client
import urllib
import argparse

# http_client.HTTPConnection.debuglevel = 1

API_BASE = 'https://www.ncbi.nlm.nih.gov/research/bionlp/litvar'


def harvest(variant_name=None, query={"disease": ['mesh@D009369']}):
    if variant_name:
        # start w/ variant
        url = '{}/api/v1/entity/search/{}'.format(API_BASE, variant_name)
        r = requests.get(url)
        for concept in r.json():
            # the first concept has the hiest weight
            # print concept['_id'], concept['weight']
            break
        variant_id = concept['_id']
        query = {'variant': [variant_id]}
    # get the relations
    url = '{}/api/v1/publications'.format(API_BASE)
    page = 0
    total_pages = 1
    while not page >= total_pages:
        page += 1
        query_request = {'query': query,
                         'facets': {},
                         'page': page, 'page_size': 15}
        r = requests.post(url, json=query_request)
        # logging.debug(query)
        result = r.json()
        if not 200 == r.status_code:
            logger.warning(result)
            break
        total_pages = result["total_pages"]
        logging.info('litvar {}/{}'.format(page, total_pages))
        count = result["count"]
        page_size = result["page_size"]
        current = result["current"]
        for hit in result['results']:
            pmid = hit['pmid']
            genes = []
            variants = []
            diseases = []
            chemicals = []
            for location_container in hit['snippets'] + hit['text']:
                seen = set([l['accession'] for l in genes])
                genes.extend([l for l in location_container['locations'] if l['concept'] == 'gene' and l['accession'] not in seen and not seen.add(l['accession'])] )
                seen = set([l['accession'] for l in variants])
                variants.extend([l for l in location_container['locations'] if l['concept'] == 'variant' and l['accession'] not in seen and not seen.add(l['accession'])])
                seen = set([l['accession'] for l in diseases])
                diseases.extend([l for l in location_container['locations'] if l['concept'] == 'disease' and l['accession'] not in seen and not seen.add(l['accession'])])
                seen = set([l['accession'] for l in chemicals])
                chemicals.extend([l for l in location_container['locations'] if l['concept'] == 'chemical' and l['accession'] not in seen and not seen.add(l['accession'])])
            descriptions = [text['text'] for text in hit['text']] +  [snippet['snippetText'] for snippet in hit['snippets']]
            descriptions = list(set(descriptions))
            for variant in variants:
                for gene in genes:
                    if 'gene_id' in variant:
                        if gene['accession'] == 'gene@{}'.format(variant['gene_id']):
                            variant['geneSymbol'] = gene['name']
            if len(genes) and (len(diseases) or len(chemicals)):
                yield {'pmids': [pmid], 'genes': genes, 'variants': variants,
                       'diseases': diseases, 'chemicals': chemicals,
                       'descriptions': descriptions, '_id': pmid}

# {
#   "diseases": [
#     {
#       "concept": "disease",
#       "name": "Neoplasms",
#       "text": "cancers",
#       "accession": "mesh@D009369",
#       "start": 28,
#       "length": 7
#     },
#     {
#       "concept": "disease",
#       "name": "Leukemia",
#       "text": "CBFbeta-MYH11 leukemia",
#       "accession": "mesh@D007938",
#       "start": 93,
#       "length": 22
#     }
#   ],
#   "genes": [
#     {
#       "concept": "gene",
#       "name": "KIT",
#       "text": "kit",
#       "accession": "gene@3815",
#       "start": 46,
#       "length": 3
#     },
#     {
#       "concept": "gene",
#       "name": "PHGDH",
#       "text": "pdg",
#       "accession": "gene@26227",
#       "start": 50,
#       "length": 3
#     }
#   ],
#   "pmids": [
#     29545943
#   ],
#   "chemicals": [
#     {
#       "concept": "chemical",
#       "name": "Dasatinib",
#       "text": "Dasatinib",
#       "accession": "mesh@C488369",
#       "start": 0,
#       "length": 9
#     }
#   ],
#   "descriptions": [
#     "Dasatinib overrides the differentiation blockage in a patient with mutant-KIT D816V positive CBFbeta-MYH11 leukemia"
#   ],
#   "variants": [
#     {
#       "concept": "variant",
#       "name": "rs121913507",
#       "text": "D816V",
#       "rsid": "rs121913507",
#       "gene_id": 3815,
#       "accession": "litvar@rs121913507##",
#       "start": 78,
#       "length": 5,
#       "hgvs": "p.D816V"
#     }
#   ]
# }


def convert(evidence):
    """ given gene data from litvar, convert it to ga4gh """
    try:
        genes = []
        for gene in evidence['genes']:
            genes.append(gene['name'])

        features = []
        for variant in evidence['variants']:
            feature = {}
            geneSymbol = variant.get('geneSymbol', None)
            if geneSymbol:
                feature['geneSymbol'] = variant.get('geneSymbol', None)
                feature['description'] = '{} {}'.format(variant.get('geneSymbol', None),
                                                        variant.get('hgvs', None))
            else:
                feature['description'] = '{}'.format(variant.get('name', None))

            feature['accession'] = variant['accession']
            features.append(feature)

        association = {}
        association['environmentalContexts'] = []
        environmentalContexts = association['environmentalContexts']
        for chemical in evidence['chemicals']:
            environmentalContexts.append({
                'description': chemical['name'],
                'accession': chemical['accession']
            })
        if len(evidence['chemicals']) > 0:
            association['drug_labels'] = ','.join(
                [chemical['name'] for chemical in evidence['chemicals']])

        association['description'] = ' '.join(evidence['descriptions'])

        association['phenotypes'] = [
            {'description': d['name'], 'accession': d['accession']} for d in evidence['diseases']
        ]

        association['evidence'] = [{
            "evidenceType": {
                "sourceName": "litvar",
                "id": evidence['_id']
            },
            'info': {
                'publications': [
                    "http://www.ncbi.nlm.nih.gov/pubmed/{}".format(pmid)
                    for pmid in evidence['pmids']
                ]
            }
        }]
        association['evidence_label'] = None
        feature_association = {'genes': genes,
                               'features': features,
                               'association': association,
                               'feature_names': [
                                    f['description'] for f in features
                                ],
                               'source': 'litvar',
                               'source_url': None,
                               'litvar': evidence}
        yield feature_association
    except Exception as e:
        logging.error(evidence, exc_info=1)


def harvest_and_convert(genes):
    """ get data from civic, convert it to ga4gh and return via yield """
    for evidence in harvest(genes):
        for feature_association in convert(evidence):
            yield feature_association
