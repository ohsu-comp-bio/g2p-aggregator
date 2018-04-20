import sys
sys.path.append('.')  # NOQA
import logging
logging.basicConfig(level=logging.DEBUG)

from biomarker_normalizer import _alias, get_soid_data, normalize
import requests
import requests_cache
# cache responses
requests_cache.install_cache('harvester')

def test_alias_fusion():
    term = 'FUS'
    alias = _alias(term)
    assert alias == 'fusion'

def test_alias_substitution():
    term = 'MUT;MUT'
    alias = _alias(term)
    assert alias == 'substitution'

def test_get_so_data():
    term = 'SO:0001880'
    soid = get_soid_data(term)
    assert soid['soid'] == term
    assert soid['name'] == 'feature_amplification'
    assert soid['parent_soid'] == 'SO:0001060'
    assert soid['parent_name'] == 'sequence_variant'
    assert len(soid['hierarchy']) == 2

def test_normalize_amp():
    term = 'amp'
    soid = normalize(term)
    assert soid['soid'] == 'SO:0001880'
    assert soid['name'] == 'feature_amplification'
    assert soid['parent_soid'] == 'SO:0001060'
    assert soid['parent_name'] == 'sequence_variant'
    assert len(soid['hierarchy']) == 2

def test_normalize_amp():
    term = 'mutant'
    soid = normalize(term)
    assert soid['soid'] == 'SO:1000002'
    assert soid['name'] == 'substitution'
    assert soid['parent_soid'] == 'SO:0000110'
    assert soid['parent_name'] == 'sequence_feature'
    assert len(soid['hierarchy']) == 3

def test_normalize_wildtype():
    term = 'wild-type'
    soid = normalize(term)
    assert soid['soid'] == 'SO:0000817'
    assert soid['name'] == 'wild_type'
    assert soid['parent_soid'] == 'SO:0000400'
    assert soid['parent_name'] == 'sequence_attribute'
    assert len(soid['hierarchy']) == 2

def test_normalize_wildtype():
    term = 'inact mut'
    soid = normalize(term)
    assert soid['soid'] == 'SO:0002054'
    assert soid['name'] == 'loss_of_function_variant'
    assert soid['parent_soid'] == 'SO:0001060'
    assert soid['parent_name'] == 'sequence_variant'
    assert len(soid['hierarchy']) == 2

def test_uncategorized():
    term = 'over exp'
    soid = normalize(term)
    assert soid == None


def test_CNA():
    term = 'CNA'
    soid = normalize(term)
    assert soid == {'hierarchy': [u'SO:0000110', u'SO:0002072', u'SO:0001059', u'SO:0000248'], 'soid': u'SO:0001019', 'parent_name': u'sequence_feature', 'name': u'copy_number_variation', 'parent_soid': u'SO:0000110'}


def test_get_so_data_0001587():
    term = 'SO:0001587'
    soid = get_soid_data(term)
    assert soid['soid'] == term
    assert soid['name'] == 'stop_gained'
    assert soid['parent_soid'] == 'SO:0001060'
    assert soid['parent_name'] == 'sequence_variant'
    assert len(soid['hierarchy']) == 10


def test_Missense_Variant():
    term = "Missense Variant"
    soid = normalize(term)
    assert soid == {'hierarchy': [u'SO:0001060', u'SO:0001537', u'SO:0001878', u'SO:0001564', u'SO:0001576', u'SO:0001791', u'SO:0001580', u'SO:0001818', u'SO:0001650', u'SO:0001992'], 'soid': u'SO:0001583', 'parent_name': u'sequence_variant', 'name': u'missense_variant', 'parent_soid': u'SO:0001060'}
