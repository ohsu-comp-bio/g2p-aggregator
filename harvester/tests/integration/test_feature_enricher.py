
import json
import sys
import time
sys.path.append('.')  # NOQA
from feature_enricher import enrich


def test_gene_enrichment():
    feature = enrich({'name': 'BRCA1'})
    assert (feature['start'])
    assert feature == {'end': 41277500, 'name': 'BRCA1', 'start': 41196312, 'referenceName': 'GRCh37', 'chromosome': '17', 'description': 'BRCA1'}


def test_gene_enrichment_JAK():
    feature = enrich({'name': 'JAK'})
    assert (feature['start'])
    assert feature == {'end': 27418537, 'name': 'JAK', 'start': 27400537, 'referenceName': 'GRCh37', 'chromosome': '17', 'description': 'JAK'}


def test_feature_enrichment():
    feature = enrich({'name': 'BRCA1 V600E'})
    assert (feature['start'])
    assert feature == {'end': 41245877, 'name': 'BRCA1 V600E', 'start': 41245877, 'biomarker_type': 'nonsense', 'referenceName': 'GRCh37', 'alt': u'A', 'ref': u'T', 'chromosome': '17', 'description': 'BRCA1 V600E'}


def test_feature_enrichment_ALK_D1203N():
    feature = enrich({'name': "ALK D1203N "})
    assert (feature['start'])
    assert feature == {'end': 29940443, 'name': 'ALK D1203N ', 'start': 29940443, 'referenceName': 'GRCh37', 'alt': u'T', 'ref': u'C', 'chromosome': '2', 'description': 'ALK D1203N '}
