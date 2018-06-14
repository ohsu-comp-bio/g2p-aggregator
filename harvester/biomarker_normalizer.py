import requests
import urllib
import os
import logging

NOFINDS = []
BIOONTOLOGY_NOFINDS = []
CACHED = {}

API_KEY = os.environ.get('BIOONTOLOGY_API_KEY')
if not API_KEY:
    raise ValueError('Please set BIOONTOLOGY_API_KEY in environment')

DATA_DIR = os.environ.get('HARVESTER_DATA', '../data')


biomarker_alias = {}
with open('{}/biomarkers.tsv'.format(DATA_DIR), 'r') as fi:
    for line in fi:
        if line.startswith('#'):
            continue
        bits = line.split('\t')
        biomarker_alias[bits[0]] = bits[1].strip('\n')


def _alias(biomarker):
    if biomarker in biomarker_alias:
        return biomarker_alias[biomarker]
    return biomarker


def _parse(txt):
    jsn = {}
    lines = txt.split('\n')
    headers = lines[0].split('\t')
    data = lines[1].split('\t')
    if len(headers) > len(data):
        headers.remove('DB_Xrefs')
    for i in range(len(headers)):
        jsn[headers[i].lower()] = data[i]
    return jsn


def get_soid_data(soid):
    """ take the sequence ontology id grabbed from
        the bioontology API and get the info about
        it from sequence ontology """
    if soid.startswith('SO'):
        try:
            url = 'http://www.sequenceontology.org/browser/current_svn/export/term_only/csv_text/{}'.format(soid)  # NOQA
            r = requests.get(url, timeout=20)
            data = _parse(r.text)
            bsubtype = {'soid': data['accession'],
                        'name': data['name'],
                        'hierarchy': []}
            if data['parents'] != '':
                # TODO: Deal with multiple parent lines up the tree.
                parent = data['parents'].split(',')[0]
                btype = get_soid_data(parent)
                if btype['hierarchy']:
                    bsubtype['root_soid'] = btype['root_soid']
                    bsubtype['root_name'] = btype['root_name']
                else:
                    bsubtype['root_soid'] = btype['soid']
                    bsubtype['root_name'] = btype['name']
                btype['hierarchy'].append(btype['soid'])
                bsubtype['hierarchy'] = btype['hierarchy']
        except:
            return None
    return bsubtype


def normalize(biomarker):
    """ take the given biomarker definition from each
        source and search through sqquence ontology
        for it """
    if biomarker in BIOONTOLOGY_NOFINDS:
        logging.info('{} in biomarker_normalizer.BIOONTOLOGY_NOFINDS'
                     .format(biomarker))
        return None

    if biomarker in CACHED:
        return CACHED[biomarker]

    btype = None
    quoted = urllib.quote_plus(_alias(biomarker))
    url = 'http://data.bioontology.org/search?q={}&apikey={}'.format(quoted, API_KEY)  # NOQA
    r = requests.get(url, timeout=20)
    response = r.json()
    for obj in response['collection']:
        parts = obj['@id'].split('/')
        idx = parts[-1]
        if parts[-2] == 'obo':
            if idx.startswith('SO'):
                btype = get_soid_data(idx.replace('_', ':'))
                break
    if btype is None:
        BIOONTOLOGY_NOFINDS.append(quoted)
    CACHED[biomarker] = btype

    return btype


def normalize_feature_association(feature_association):
    """ given a 'final' g2p feature_association,
        update it to normalize biomarker type by
        sequence ontology """
    # nothing to normalize? return
    for feat in feature_association['features']:
        if 'biomarker_type' not in feat:
            continue
        btype = normalize(feat['biomarker_type'])
        if btype is None:
            feature_association['dev_tags'].append('no-so')
            feat['sequence_ontology'] = {
                'soid': '',
                'name': 'Uncategorized',
                'root_soid': '',
                'root_name': 'Uncategorized',
            }
            continue
        # Currently only dealing with a exact matches
        # Assuming we have a match, add to feature_association
        feat['sequence_ontology'] = btype
        # return asso to main harvester
