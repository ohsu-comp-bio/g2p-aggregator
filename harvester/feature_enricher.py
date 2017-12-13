import json
import requests
import os
import mutation_type as mut


def enrich(feature):
    """
    given a feature, decorate it with genomic location
    """
    apiKey = os.environ.get('MOLECULAR_MATCH_API_KEY')
    if not apiKey:
        raise ValueError('Please set MOLECULAR_MATCH_API_KEY in environment')

    url = "https://api.molecularmatch.com/v2/mutation/get"
    headers = {'Authorization': 'Bearer {}'.format(apiKey)}
    payload = {'name': feature['description']}
    r = requests.get(url, params=payload, headers=headers)
    mutation = r.json()
    if 'name' in mutation:
        feature['name'] = mutation['name']
    else:
        feature['name'] = feature['description']
    if ('GRCh37_location' in mutation and
            len(mutation['GRCh37_location']) > 0):
        grch37_mutation = mutation['GRCh37_location'][0]
        if 'ref' in grch37_mutation:
            feature['ref'] = grch37_mutation['ref']
        if 'alt' in grch37_mutation:
            feature['alt'] = grch37_mutation['alt']
        if 'chr' in grch37_mutation:
            feature['chromosome'] = str(grch37_mutation['chr'])
        if 'start' in grch37_mutation:
            feature['start'] = grch37_mutation['start']
        if 'stop' in grch37_mutation:
            feature['end'] = grch37_mutation['stop']

        feature['referenceName'] = 'GRCh37'
        links = feature.get('links', [])
        links.append(r.url)
        feature['links'] = links

    if 'biomarker_type' not in feature:
        if ('mutation_type' in mutation and
                len(mutation['mutation_type']) > 0):
                feature['biomarker_type'] = mut.norm_biomarker(
                                mutation['mutation_type'][0])

    # there is a lot of info in mutation, just get synonyms and links
    if ('wgsaMap' in mutation and 'Synonyms' in mutation['wgsaMap'][0]):
        synonyms = feature.get('synonyms', [])
        synonyms = synonyms + mutation['wgsaMap'][0]['Synonyms']
        synonyms = list(set(synonyms))
        feature['synonyms'] = synonyms

    # if 'geneSymbol' in mutation and mutation['geneSymbol']:
    #     feature['geneSymbol'] = mutation['geneSymbol']

    return feature
