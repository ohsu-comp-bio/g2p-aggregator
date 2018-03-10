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
        if 'provenance' not in feature:
            feature['provenance'] = []
        feature['provenance'].append(url)
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
        if 'provenance' not in feature:
            feature['provenance'] = []
        feature['provenance'].append(url)

        if 'biomarker_type' not in feature:
            if 'cadd' in hit and 'type' in hit['cadd']:
                feature['biomarker_type'] = \
                    mut.norm_biomarker(hit['cadd']['type'])

    return feature


def enrich(feature):
    """
    given a feature, decorate it with genomic location
    """
    try:
        # return if already there
        if feature.get('start', None):
            return feature

        # make sure it has a name and a description
        if not feature.get('description', None):
            feature['description'] = feature.get('name', None)
        if not feature.get('name', None):
            feature['name'] = feature.get('description', None)

        # we can't normalize things without a description
        if not feature.get('description', None):
            return feature

        # we can't normalize things without a description
        description_parts = re.split(' +', feature['description'].strip())
        description_length = len(description_parts)
        if description_length == 1:
            feature = _enrich_gene(feature)
        else:
            feature = _enrich_feature(feature)
    except Exception as e:
        logging.error(feature, exc_info=1)

    return feature
