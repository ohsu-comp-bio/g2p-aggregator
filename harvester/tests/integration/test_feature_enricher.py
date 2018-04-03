
import json
import sys
import time
sys.path.append('.')  # NOQA
from feature_enricher import enrich


def test_gene_enrichment():
    feature = enrich({'name': 'BRCA1'}, {})[0]
    assert (feature['start'])
    assert feature == {'provenance_rule': 'gene_only', 'end': 41277500, 'name': 'BRCA1', 'provenance': ['http://mygene.info/v3/query?q=BRCA1&fields=genomic_pos_hg19'], 'start': 41196312, 'referenceName': 'GRCh37', 'chromosome': '17', 'description': 'BRCA1'}


def test_feature_enrichment():
    feature = enrich({'name': 'BRCA1 V600E'}, {})[0]
    assert (feature['start'])
    assert feature == {'provenance_rule': 'default_feature', 'end': 41245877, 'name': 'BRCA1 V600E', 'provenance': ['http://myvariant.info/v1/query?q=BRCA1 V600E'], 'start': 41245877, 'biomarker_type': 'nonsense', 'referenceName': 'GRCh37', 'alt': u'A', 'ref': u'T', 'chromosome': '17', 'description': 'BRCA1 V600E'}

def test_gene_enrichment_JAK():
    feature = enrich({'name': 'JAK'}, {})[0]
    assert (feature['start'])
    assert feature == {'provenance_rule': 'gene_only', 'end': 27418537, 'name': 'JAK', 'provenance': ['http://mygene.info/v3/query?q=JAK&fields=genomic_pos_hg19'], 'start': 27400537, 'referenceName': 'GRCh37', 'chromosome': '17', 'description': 'JAK'}
