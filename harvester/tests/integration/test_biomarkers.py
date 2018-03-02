import sys
sys.path.append('.')  # NOQA
import logging
import mutation_type as mut
import os
import requests
import requests_cache
requests_cache.install_cache('biomarkers', allowable_codes=(200, 404))


BIOMARKERS = ['SO:0001623', 'SO:0001624', 'SO:0000105', 'SO:0000129', 'SO:0000159', 'SO:0000159', 'SO:0000162', 'SO:0000289', 'SO:0000289', 'SO:0000417', 'SO:0000475', 'SO:0000667', 'SO:0000667', 'SO:0000667', 'SO:0000694', 'SO:0000694', 'SO:0000806', 'SO:0000806', 'SO:0000817', 'SO:0000817', 'SO:0000817', 'SO:0000865', 'SO:0000865', 'SO:0000891', 'SO:0001017', 'SO:0001019', 'SO:0001025', 'SO:0001429', 'SO:0001549', 'SO:0001563', 'SO:0001564', 'SO:0001565', 'SO:0001566', 'SO:0001566', 'SO:0001572', 'SO:0001574', 'SO:0001574', 'SO:0001575', 'SO:0001576', 'SO:0001578', 'SO:0001580', 'SO:0001580', 'SO:0001583', 'SO:0001583', 'SO:0001583', 'SO:0001583', 'SO:0001587', 'SO:0001587', 'SO:0001587', 'SO:0001587', 'SO:0001589', 'SO:0001589', 'SO:0001589', 'SO:0001589', 'SO:0001592', 'SO:0001594', 'SO:0001604', 'SO:0001627', 'SO:0001627', 'SO:0001628', 'SO:0001630', 'SO:0001650', 'SO:0001650', 'SO:0001743', 'SO:0001784', 'SO:0001786', 'SO:0001791', 'SO:0001815', 'SO:0001818', 'SO:0001818', 'SO:0001819', 'SO:0001820', 'SO:0001821', 'SO:0001821', 'SO:0001822', 'SO:0001822', 'SO:0001826', 'SO:0001880', 'SO:0001886', 'SO:0001889', 'SO:0001889', 'SO:0001890', 'SO:0001893', 'SO:0001893', 'SO:0001906', 'SO:0001906', 'SO:0001909', 'SO:0001910', 'SO:0001968', 'SO:0001969', 'SO:0001992', 'SO:0002012', 'SO:0002012', 'SO:0002015', 'SO:0002052', 'SO:0002053', 'SO:0002053', 'SO:0002054', 'SO:0002054', 'SO:0002092', 'SO:0002096', 'SO:0002186', 'SO:1000032', 'SO:0000667', 'SO:0002054', 'SO:0000159', ]  # NOQA

API_KEY = os.environ.get('BIOONTOLOGY_API_KEY')
if not API_KEY:
    raise ValueError('Please set BIOONTOLOGY_API_KEY in environment')


def _biomarker(s):
    try:
        return mut.norm_biomarker(s)
    except Exception as e:
        return 'Exception:{}'.format(e)


def _so(s):
    url = 'http://data.bioontology.org/search?q={}&ontologies=SO&apikey={}&require_exact_match=true'.format(s, API_KEY)  # NOQA
    r = requests.get(url, timeout=20)
    response = r.json()
    if 'collection' in response and len(response['collection']) > 0:
        return (response['collection'][0]['prefLabel'],
                response['collection'][0]['@id'],
                'exact')
    url = 'http://data.bioontology.org/search?q={}&ontologies=SO&apikey={}&require_exact_match=false'.format(s, API_KEY)  # NOQA
    r = requests.get(url, timeout=20)
    response = r.json()
    if 'collection' in response and len(response['collection']) > 0:
        return (response['collection'][0]['prefLabel'],
                response['collection'][0]['@id'],
                'synonym')
    return None


def _so_parent(s):
    url = 'http://data.bioontology.org/ontologies/SO/classes/{}/ancestors?apikey={}'.format(s, API_KEY)  # NOQA
    r = requests.get(url, timeout=20)
    response = r.json()
    try:
        if len(response) > 0:
            if 'prefLabel' in response[0]:
                return (response[0]['prefLabel'],
                        response[0]['@id'])
            else:
                return ('no prefLabel')
    except Exception as e:
        print response
        raise e


def _so_ancestor(s):
    url = 'http://data.bioontology.org/ontologies/SO/classes/{}/ancestors?apikey={}'.format(s, API_KEY)  # NOQA
    r = requests.get(url, timeout=20)
    response = r.json()
    try:
        if len(response) > 0:
            if 'prefLabel' in response[-2]:
                return (response[-2]['prefLabel'],
                        response[-2]['@id'])
            else:
                return ('no prefLabel')
    except Exception as e:
        print response
        raise e


def test_all_biomarkers():
    with open('./tests/integration/biomarkers.tsv', 'r') as tsv:
        biomarkers = [line.strip().split('\t') for line in tsv]
    for biomarker in biomarkers:
        so = _so(biomarker[1])
        if so:
            so = '{}\t{}\t{}\t'.format(so[0], so[1], so[2])
        print '{}\t{}\t{}\t{}'.format(biomarker[0],
                                      biomarker[1],
                                      _biomarker(biomarker[1]),
                                      so)


def test_biomarker_parent():
    for biomarker in BIOMARKERS:
        parent = _so_parent(biomarker)
        print '{}\t{}'.format(parent[0], parent[1].replace('http://purl.obolibrary.org/obo/SO_','SO:'))


def test_biomarker_ancestors():
    for biomarker in BIOMARKERS:
        ancestor = _so_ancestor(biomarker)
        print '{}\t{}'.format(ancestor[0], ancestor[1].replace('http://purl.obolibrary.org/obo/SO_','SO:'))
