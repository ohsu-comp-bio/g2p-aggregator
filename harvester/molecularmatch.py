
import requests
import json
import os


# curl 'http://api-demo.molecularmatch.com/v2/search/assertions' --data 'apiKey=xxxxxxxxx' --data-urlencode 'filters=[{"facet":"MUTATION","term":"KIT"}]'
resourceURLs = {
    "assertions": "/v2/search/assertions"
}
mmService = "http://api-demo.molecularmatch.com"


apiKey = os.environ.get('MOLECULAR_MATCH_API_KEY')


def get_evidence(gene_ids=['KIT']):
    """ load from remote api """
    if not apiKey:
        raise ValueError('Please set MOLECULAR_MATCH_API_KEY in environment')
    # first look for all drugs that impact this gene
    for gene in gene_ids:
        url = mmService + resourceURLs["assertions"]
        filters = [{'facet': 'MUTATION',
                    'term': '{}.*'.format(gene)
                    }]
        payload = {
            'apiKey': apiKey,
            'filters': json.dumps(filters)
        }
        try:
            r = requests.post(url, data=payload)
            assertions = r.json()

            # filter those drugs, only those with diseases
            for hit in assertions['hits']:
                if gene in hit['narrative']:
                    yield hit
        except Exception as e:
            print "molecularmatch error fetching {} {}".format(gene, e)


def convert(evidence):
    """

    """
    sources = evidence['sources']
    tier = evidence['tier']
    direction = evidence['direction']
    narrative = evidence['narrative']
    therapeuticContext = evidence['therapeuticContext']
    clinicalSignificance = evidence['clinicalSignificance']
    tags = evidence['tags']
    gene = None
    condition = None
    mutation = None
    for tag in tags:
        if tag['facet'] == 'GENE':
            gene = tag['term']
        if tag['facet'] == 'CONDITION':
            condition = tag['term']
        if tag['facet'] == 'MUTATION':
            mutation = tag['term']
    if not gene and mutation:
        gene = mutation.split(' ')[0]

    feature = {}
    feature['geneSymbol'] = gene
    feature['name'] = mutation

    association = {}
    association['description'] = narrative
    association['environmentalContexts'] = []
    association['environmentalContexts'].append({
        'description': therapeuticContext[0]['name']})
    association['phenotype'] = {
        'description': condition
    }

    pubs = []
    for p in sources:
        pubs.append(p['link'])

    association['evidence'] = [{
        "evidenceType": {
            "sourceName": "molecularmatch"
        },
        'description': narrative,
        'info': {
            'publications': pubs
        }
    }]
    # add summary fields for Display
    association['evidence_label'] = direction
    association['publication_url'] = pubs[0]
    association['drug_labels'] = therapeuticContext[0]['name']
    feature_association = {'gene': gene,
                           'feature': feature,
                           'association': association,
                           'source': 'molecularmatch',
                           'molecularmatch': evidence}
    yield feature_association


def harvest(genes):
    """ get data from mm """
    for evidence in get_evidence(genes):
        yield evidence


def harvest_and_convert(genes):
    """ get data from mm, convert it to ga4gh and return via yield """
    for evidence in harvest(genes):
        # print "harvester_yield {}".format(evidence.keys())
        # print evidence
        for feature_association in convert(evidence):
            # print "mm convert_yield {}".format(feature_association.keys())
            yield feature_association


def test():
    gene_ids = ["CCND1", "CDKN2A", "CHEK1", "DDR2", "FGF19", "FGF3", "FGF4", "FGFR1", "MDM4", "PALB2", "RAD51D"]
    for feature_association in harvest_and_convert(gene_ids):
        print feature_association.keys()
        print json.dumps(feature_association, indent=2)
        break

    # for evidence in harvest(gene_ids):
    #     #print evidence['narrative']
    #     print json.dumps(evidence, indent=2)
    #     break

if __name__ == '__main__':
    test()

