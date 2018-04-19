import sys
from attrdict import AttrDict
sys.path.append('.')  # NOQA
import smmart  # NOQA



def test_harvest():
    rows = [row for row in smmart.harvest()]
    assert rows


def test_convert():
    for row in smmart.harvest():
        for feature_association in smmart.convert(row):
            feature_association = AttrDict(feature_association)
            assert(feature_association.genes)
            assert(feature_association.features)
            assert(feature_association.association)
            assert(feature_association.association.evidence)
            assert(feature_association.source == 'smmart')
            assert(feature_association.smmart)
