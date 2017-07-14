import sys
sys.path.append('.')  # NOQA

from drug_normalizer import normalize, normalize_chembl
import requests
import requests_cache
import logging
# logging.basicConfig(level=logging.WARNING)

# cache responses
requests_cache.install_cache('harvester')


def test_nonsense():
    compounds = normalize('HHDHDHDHDHD')
    assert len(compounds) == 0


def test_decorated_name():
    compounds = normalize("Dasatinib (BCR-ABL inhibitor 2nd gen)")
    assert compounds[0]['ontology_term'] == 'compound:CID3062316'
    assert compounds[0]['synonym'] == 'Dasatinib'


def test_combination():
    compounds = normalize("Trametinib + Dabrafenib")
    assert len(compounds) == 2
    assert compounds[0]['ontology_term'] == 'compound:CID11707110'
    assert compounds[0]['synonym'] == 'Trametinib'
    assert compounds[1]['ontology_term'] == 'compound:CID44462760'
    assert compounds[1]['synonym'] == 'Dabrafenib'


def test_celecoxib():
    compounds = normalize('celecoxib')
    assert compounds[0]['ontology_term'] == 'compound:CID2662'
    assert compounds[0]['synonym'] == 'Celecoxib'


def test_chembl_asprin():
    compounds = normalize_chembl('asprin')
    assert compounds[0]['ontology_term'] == 'compound:CHEMBL25'
    assert compounds[0]['synonym'] == 'ASPIRIN'


def test_chembl_bayer():
    compounds = normalize_chembl('Bayer')
    assert len(compounds) == 0


def test_chembl_ASN003():
    compounds = normalize_chembl('ASN003')
    assert len(compounds) == 0


def test_chembl_DHM25():
    compounds = normalize_chembl('DHM25')
    assert len(compounds) == 0


def test_chembl_HDAC_inhibitors():
    compounds = normalize_chembl('HDAC inhibitors')
    assert len(compounds) == 0


def test_cgi_drug_full_name():
    compounds = normalize('Imatinib (BCR-ABL inhibitor 1st gen&KIT inhibitor)')
    assert len(compounds) == 1


def test_cgi_drug_plus_drug():
    compounds = normalize('Cetuximab+Vemurafenib')
    assert len(compounds) == 2


def test_gefintinib():
    compounds = normalize('gefintinib')
    assert len(compounds) == 0


def test_gefitnib():
    compounds = normalize('gefitnib')
    assert len(compounds) == 0


def test_dacomitinib():
    compounds = normalize('Dacomitinib')
    assert len(compounds) == 1


def test_Vemurafenib():
    compounds = normalize('Vemurafenib')
    assert len(compounds) == 1
    assert compounds[0] == {'approved_countries': ['Canada', 'US'],
                            'synonym': 'Vemurafenib',
                            'ontology_term': 'compound:CID42611257',
                            'taxonomy': {'class': 'Pyridines and derivatives',
                                         'direct-parent': 'Phenylpyridines',
                                         'kingdom': 'Organic compounds',
                                         'subclass': 'Phenylpyridines',
                                         'superclass':
                                         'Organoheterocyclic compounds'}
                            }
