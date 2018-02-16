#!/usr/bin/python
# -*- coding: utf-8 -*-
import genes
import local
import logging

# biostream-schema
from bmeg.clinical_pb2 import *
from bmeg.cna_pb2 import *
from bmeg.genome_pb2 import *
from bmeg.phenotype_pb2 import *
from bmeg.rna_pb2 import *
from bmeg.variants_pb2 import *
from google.protobuf import json_format
import json
from google.protobuf.json_format import MessageToJson

logger = logging.getLogger(__name__)
# keep track of what we've already exported
exported = []


def feature_gid(f):
    """ given a feature, hash it"""
    a = []
    empty_count = 0
    gid_name = ''  # no 'variant:' as start
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
            gid_name = 'gene'
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
    if 'alt' in feature and feature['alt']:
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
    ttl = normalize({'features': [
        {
            "geneSymbol": "TTL"
        }
    ]})
    assert ({'features': ['ENSG00000114999']}, {'ENSG00000114999': {'id': 'ENSG00000114999', 'names': []}}) == ttl    # noqa
    complex_rsp = normalize({'features': [
        COMPLEX_FEATURE,
    ]})
    # print complex_rsp
    assert ({'features': ['GRCh37:4:55593607:55593615:AGGTTGTTG:-']}, {'GRCh37:4:55593607:55593615:AGGTTGTTG:-': {'end': 55593615, 'reference_genome': 'GRCh37', 'reference_name': '4', 'alternate_bases': ['-'], 'reference_bases': 'AGGTTGTTG', 'start': 55593607, 'variant_type': 'nonsense', 'names': ['KIT V559_E561del'], 'id': 'GRCh37:4:55593607:55593615:AGGTTGTTG:-'}}) == complex_rsp  # noqa

    complex_ttl = normalize({'features': [
        {
            "geneSymbol": "TTL"
        },
        COMPLEX_FEATURE
    ]})
    assert ({'features': ['GRCh37:4:55593607:55593615:AGGTTGTTG:-', 'ENSG00000114999']}, {}) == complex_ttl   # noqa

    v = Variant()
    o = json_format.Parse(json.dumps(complex_rsp[1]['GRCh37:4:55593607:55593615:AGGTTGTTG:-']), v, ignore_unknown_fields=False)
    assert(MessageToJson(o))
