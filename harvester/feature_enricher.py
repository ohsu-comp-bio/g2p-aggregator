import json
import requests
import os
import mutation_type as mut
import logging
import re


def _enrich_gene(feature):
    """ description contains a gene, get its location """
    url = "http://mygene.info/v3/query?q={}&fields=genomic_pos_hg19".format(feature['description'])
    r = requests.get(url, timeout=60)
    hit = None
    hits = r.json()
    if 'hits' in hits:
        for a_hit in hits['hits']:
            if 'genomic_pos_hg19' in a_hit:
                hit = a_hit['genomic_pos_hg19']
                break
    if hit:
        if 'chr' in hit:
            feature['chromosome'] = str(hit['chr'])
        if 'start' in hit:
            feature['start'] = hit['start']
        if 'end' in hit:
            feature['end'] = hit['end']
        feature['referenceName'] = 'GRCh37'
    return feature


def _enrich_feature(feature):
    """ description contains a gene + variant, get its location """
    #  curl -s http://myvariant.info/v1/query?q=FLT3%20N676D |
    # jq '.hits[0] |
    # { referenceName: "GRCh37", chromosome: .chrom,
    # start: .hg19.start, end: .hg19.end, ref: .vcf.ref, alt: .vcf.alt  }'
    # {
    #   "referenceName": "GRCh37",
    #   "chromosome": "13",
    #   "start": 28644637,
    #   "end": 28644637,
    #   "ref": "T",
    #   "alt": "A"
    # }
    url = "http://myvariant.info/v1/query?q={}".format(feature['description'])
    r = requests.get(url, timeout=60)
    hits = r.json()
    hit = None
    if 'hits' in hits:
        for a_hit in hits['hits']:
            if 'hg19' in a_hit and 'vcf' in a_hit:
                hit = a_hit
                break
    if hit:
        hg19 = hit.get('hg19')
        vcf = hit.get('vcf')
        if 'ref' in vcf:
            feature['ref'] = vcf['ref']
        if 'alt' in vcf:
            feature['alt'] = vcf['alt']
        if 'chrom' in hit:
            feature['chromosome'] = str(hit['chrom'])
        if 'start' in hg19:
            feature['start'] = hg19['start']
        if 'end' in hg19:
            feature['end'] = hg19['end']
        feature['referenceName'] = 'GRCh37'

        if 'biomarker_type' not in feature:
            if 'cadd' in hit and 'type' in hit['cadd']:
                feature['biomarker_type'] = \
                    mut.norm_biomarker(hit['cadd']['type'])

    return feature


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
