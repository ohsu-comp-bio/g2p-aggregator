#!/usr/bin/python
# -*- coding: utf-8 -*-
import genes
import local
import logging
logger = logging.getLogger(__name__)
# keep track of what we've already exported
exported = []


def feature_gid(f):
    """ given a feature, hash it"""
    a = []
    empty_count = 0
    gid_name = 'variant:'
    for p in ['referenceName', 'chromosome', 'start',
              'end', 'ref', 'alt']:
        a.append(str(f.get(p, '')))
    if 'start' not in f:
        a = []
        geneSymbol = f.get('geneSymbol', None)
        if geneSymbol:
            gene_name = genes.gene_lookup(geneSymbol)
            if gene_name:
                a.append(gene_name.id)
            else:
                logger.warn('no ensembl for {}'.format(geneSymbol))
        description = f.get('description', None)
        if not description:
            gid_name = 'gene:'
        else:
            a.append(description)
    return gid_name + ':'.join(a)


def _variant(feature, gid):
    v = {
        'id': gid,
    }
    v['names'] = []
    if 'synonyms' in feature:
        v['names'].extend(feature['synonyms'])
    if 'links' in feature:
        v['names'].extend(feature['links'])
    if 'name' in feature:
        v['names'].append(feature['name'])
    if 'entrez_id' in feature:
        v['names'].append(str(feature['entrez_id']))
    if 'biomarker_type' in feature:
        v['variant_type'] = feature['biomarker_type']
    if 'start' in feature:
        v['start'] = feature['start']
    if 'end' in feature:
        v['end'] = feature['end']
    if 'chromosome' in feature:
        v['reference_name'] = feature['chromosome']
    if 'referenceName' in feature:
        v['reference_genome'] = feature['referenceName']
    if 'ref' in feature:
        v['reference_bases'] = feature['ref']
    if 'alt' in feature:
        v['alternate_bases'] = [feature['alt']]

    return v


def normalize(hit):
    """ returns a tuple of (hit, features), where hit has been modified to
    normalize hit.features[] and the  features[] array
    contains features observed in this hit that have not yet been returned
    """
    features = {}
    remove_from_hit = []
    already_exported = []
    # hash each feature
    for feature in hit['features']:
        gid = feature_gid(feature)
        features[gid] = _variant(feature, gid)
    hit['features'] = list(features.keys())
    for k in features.keys():
        if k in exported:
            del features[k]
    exported.extend(features.keys())
    return (hit, features)


if __name__ == '__main__':
    """ testing """
    COMPLEX_FEATURE = \
        {
          "end": 55593615,
          "description": "KIT V559_E561del",
          "start": 55593607,
          "biomarker_type": "nonsense",
          "referenceName": "GRCh37",
          "alt": "-",
          "ref": "AGGTTGTTG",
          "chromosome": "4",
          "name": "KIT V559_E561del"
        }
    assert ({'features': ['gene:ENSG00000114999']}, {'gene:ENSG00000114999': {'geneSymbol': 'TTL'}}) == normalize({'features': [   # noqa
        {
        "geneSymbol": "TTL"
        }
    ]})
    assert ({'features': ['feature:GRCh37:4:55593607:55593615:AGGTTGTTG:-']}, {'feature:GRCh37:4:55593607:55593615:AGGTTGTTG:-': {'start': 55593607, 'end': 55593615, 'description': 'KIT V559_E561del', 'name': 'KIT V559_E561del', 'referenceName': 'GRCh37', 'alt': '-', 'ref': 'AGGTTGTTG', 'chromosome': '4', 'biomarker_type': 'nonsense'}}) == normalize({'features': [  # noqa
        COMPLEX_FEATURE,
    ]})

    complex_ttl = normalize({'features': [
        {
            "geneSymbol": "TTL"
        },
        COMPLEX_FEATURE
    ]})
    assert ({'features': ['feature:GRCh37:4:55593607:55593615:AGGTTGTTG:-', 'gene:ENSG00000114999']}, {}) == complex_ttl   # noqa
