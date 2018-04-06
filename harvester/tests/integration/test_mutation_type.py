import sys
sys.path.append('.')  # NOQA
import json
from mutation_type import norm_biomarker

MM_MUTATION_TYPES = [
    'Block Substitution',
    'CSQN=Frameshift',
    'CSQN=Unclassified',
    'Chromosome Arm',
    'Coding Sequence Variant',
    'Complex',
    'Copy Number Variant',
    'Deletion',
    'Frame Shift',
    'Fusion',
    'Gain of Function',
    'In Frame',
    'Insertion',
    'Intergenic',
    'Intron Variant',
    'Loss of Function',
    'Microsatellite',
    'Missense',
    'Non Sense',
    'Parent Mutation',
    'Promoter Variant',
    'Protein Altering Variant',
    'Regulatory Region Variant',
    'Snp',
    'Splice Acceptor Variant',
    'Splice Site',
    'Synonymous',
    'Transcript Ablation',
    'Transcript Amplification',
    'Unclassified',
    'Unknown',
    'Wild Type',
    'domain',
    'hotspot'
]


def test_molecular_match_mutation_types():
    for mutation_type in MM_MUTATION_TYPES:
        assert norm_biomarker(mutation_type) is not None


def test_molecular_match_CNA():
    print '"{}"={}'.format('Copy Number Variant',
                           norm_biomarker('Copy Number Variant'))
    assert 'copy number variant' == norm_biomarker('Copy Number Variant')


def test_CNA():
    print '"{}"={}'.format('CNA',
                           norm_biomarker('CNA'))
    assert 'copy number variant' == norm_biomarker('Copy Number Variant')
