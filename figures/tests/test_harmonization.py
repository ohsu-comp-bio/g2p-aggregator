import os
import sys
sys.path.append('./scripts')  # NOQA

from harmonization import Harmonizations
from overlaps import Overlaps

HOST = 'localhost'
INDEX = 'associations'


def test_harmonization_percentages_df():
    """ ensure df shape """
    h = Harmonizations(es_host=HOST, index=INDEX)
    percentages = h.harmonization_percentages()
    assert percentages.shape == (10, 4)


def test_harmonization_percentages_figure():
    """ ensure image file is created """
    h = Harmonizations(es_host=HOST, index=INDEX)
    assert h.harmonization_percentages_figure() is not None
    path = './images/Test.png'
    assert h.harmonization_percentages_figure(path=path)
    assert os.path.isfile(path)
    os.remove(path)


def test_feature_overlap_df():
    """ ensure df shape """
    o = Overlaps(es_host=HOST, index=INDEX)
    feature_overlaps = o.feature_overlaps()
    assert feature_overlaps.shape == (9, 9)


def test_feature_overlap_figure():
    """ ensure image file is created """
    o = Overlaps(es_host=HOST, index=INDEX)
    path = './images/Test.png'
    assert o.feature_overlaps_figure(path=path)
    assert os.path.isfile(path)
    os.remove(path)


def test_publication_overlap_df():
    """ ensure df shape """
    o = Overlaps(es_host=HOST, index=INDEX)
    publication_overlaps = o.publication_overlaps()
    assert publication_overlaps.shape == (9, 9)


def test_publication_overlap_figure():
    """ ensure image file is created """
    o = Overlaps(es_host=HOST, index=INDEX)
    path = './images/Test.png'
    assert o.feature_overlaps_figure(path=path)
    assert os.path.isfile(path)
    os.remove(path)
