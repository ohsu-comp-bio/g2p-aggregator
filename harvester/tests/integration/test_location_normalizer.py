
import json
import sys
import time
sys.path.append('.')  # NOQA
from location_normalizer import normalize_feature_association
from location_normalizer import complement, reverse_complement


def test_normalize_feature_association_ALK_D1203N():
    fa = {
        'features': [
            {
              "geneSymbol": "ALK",
              "name": "ALK D1203N "
            }
        ]
    }
    normalize_feature_association(fa)
    assert fa == {'features': [{'provenance_rule': 'default_feature', 'end': 29940443, 'name': 'ALK D1203N ', 'links': [u'http://reg.genome.network/allele/CA346587606', u'http://reg.genome.network/refseq/RS000050', u'http://reg.genome.network/refseq/RS000026', u'http://reg.genome.network/refseq/RS000002', u'http://myvariant.info/v1/variant/chr2:g.29940443C>T?assembly=hg19', u'http://myvariant.info/v1/variant/chr2:g.29717577C>T?assembly=hg38', u'http://cancer.sanger.ac.uk/cosmic/mutation/overview?id=309051', u'http://reg.genome.network/refseq/RS001597'], 'provenance': ['http://myvariant.info/v1/query?q=ALK D1203N ', 'http://reg.genome.network/allele?hgvs=NC_000002.11%3Ag.29940443C%3ET'], 'start': 29940443, 'synonyms': [u'LRG_488:g.208990G>A', u'chr2:g.29717577C>T', u'NC_000002.10:g.29793947C>T', u'CM000664.1:g.29940443C>T', u'chr2:g.29940443C>T', u'NC_000002.12:g.29717577C>T', u'NC_000002.11:g.29940443C>T', u'CM000664.2:g.29717577C>T', u'COSM309051', u'NG_009445.1:g.208990G>A'], 'referenceName': 'GRCh37', 'geneSymbol': 'ALK', 'alt': u'T', 'ref': u'C', 'chromosome': '2', 'description': 'ALK D1203N '}]}


def test_normalize_feature_association_AR_amplification():
    fa = {
        'features': [
            {
              "name": 'AR amplification'
            }
        ]
    }
    normalize_feature_association(fa)
    assert fa == {'features': [{'provenance_rule': 'is_amplification', 'end': 66950461, 'name': 'AR amplification', 'provenance': ['http://mygene.info/v3/query?q=AR&fields=genomic_pos_hg19'], 'start': 66764465, 'referenceName': 'GRCh37', 'chromosome': 'X', 'description': 'AR amplification'}]}


def test_normalize_feature_association_ABL1_BCR_fusion():
    fa = {
        'features': [
            {
              "name": "ABL1-BCR fusion"
            }
        ]
    }
    normalize_feature_association(fa)
    print fa
    assert len(fa['features']) == 2


def test_complement():
    assert 'GATC-' == complement('CTAG-')


def test_reverse_complement():
    assert '-CTAG' == reverse_complement('CTAG-')
    assert '-CG' == reverse_complement('CG-')
    assert 'TA-' == reverse_complement('-TA')
