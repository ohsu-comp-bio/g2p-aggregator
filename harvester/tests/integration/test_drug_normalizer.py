import sys
sys.path.append('.')  # NOQA

from drug_normalizer import normalize
import requests
import requests_cache
# cache responses
requests_cache.install_cache('harvester')


# def test_bayer():
#     compounds = normalize('Bayer')
#     assert compounds[0]['ontology_term'] == 'compound:CID2244'
#     assert compounds[0]['synonym'] == 'aspirin'


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
