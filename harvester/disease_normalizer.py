import requests
import urllib
import logging
import re
import os


NOFINDS = []
BIOONTOLOGY_NOFINDS = []

API_KEY = os.environ.get('BIOONTOLOGY_API_KEY')
if not API_KEY:
    raise ValueError('Please set BIOONTOLOGY_API_KEY in environment')

DATA_DIR = os.environ.get('HARVESTER_DATA', '../data')


disease_alias = {}
with open('{}/disease_alias.tsv'.format(DATA_DIR), "r") as f:
    for line in f:
        if line.startswith("#"):
            continue
        inline_list = line.rstrip().split('\t')
        disease_alias[inline_list[0].lower()] = inline_list[1]


def normalize_bioontology(name):
    """ call bioontology & retrieve """
    if name in BIOONTOLOGY_NOFINDS:
        logging.info('{} in disease_normalizer.BIOONTOLOGY_NOFINDS'
                     .format(name))
        return []
    quoted_name = urllib.quote_plus(name)
    url = 'http://data.bioontology.org/search?q={}&apikey={}'.format(quoted_name, API_KEY)  # NOQA
    r = requests.get(url, timeout=20)
    response = r.json()
    terms = []
    if 'collection' in response and len(response['collection']) > 0:
        collection = response['collection'][0]
        parts = collection['@id'].split('/')
        ontology = parts[-2]
        id = parts[-1]
        if ontology == 'obo':
            (ontology, id) = id.split('_')
        term = {'ontology_term': '{}:{}'.format(ontology, id),
                'label': name,
                'source': ontology}
        terms.append(term)
        family = get_family(term['ontology_term'])
        if family:
            term['family'] = family
    else:
        BIOONTOLOGY_NOFINDS.append(name)
    return terms


def normalize_ebi(name):
    """ call ebi & retrieve """
    if name in NOFINDS:
        # logging.info('{} in disease_normalizer.NOFINDS'.format(name))
        return []
    name = urllib.quote_plus(name)
    url = 'https://www.ebi.ac.uk/ols/api/search?q={}&groupField=iri&exact=on&start=0&ontology=doid'.format(name)  # NOQA
    # .response
    """
    {
      "numFound": 1,
      "start": 0,
      "docs": [
        {
          "id": "doid:http://purl.obolibrary.org/obo/DOID_1909",
          "iri": "http://purl.obolibrary.org/obo/DOID_1909",
          "short_form": "DOID_1909",
          "obo_id": "DOID:1909",
          "label": "melanoma",
          "description": [
            "A cell type cancer that has_material_basis_in abnormally proliferating cells derives_from melanocytes which are found in skin, the bowel and the eye."
          ],
          "ontology_name": "doid",
          "ontology_prefix": "DOID",
          "type": "class",
          "is_defining_ontology": true
        }
      ]
    }

    """  # NOQA

    r = requests.get(url, timeout=20)
    rsp = r.json()
    if 'response' not in rsp:
        logging.info('{} in disease_normalizer.NOFINDS'.format(name))
        NOFINDS.append(name)
        return []
    response = rsp['response']
    numFound = response['numFound']
    if numFound == 0:
        logging.info('{} in disease_normalizer.NOFINDS'.format(name))
        NOFINDS.append(name)
        return []
    doc = response['docs'][0]
    # check whether returned info is actually DOID or some other response
    # since we only want DOID entries
    if doc['obo_id'][:2] != 'DO':
        logging.info('{} in disease_normalizer.NOFINDS'.format(name))
        NOFINDS.append(name)
        return []
    term = {'ontology_term': doc['obo_id'].encode('utf8'),
            'label': doc['label'].encode('utf8'),
            'source': doc['iri'].encode('utf8')}
    family = get_family(doc['obo_id'])
    if family:
        term['family'] = family

    return [term]


def get_family(ontology_id):
    # get the hierarchy
    url = r = None
    try:
        if ontology_id.startswith('DOID'):
            url = 'http://disease-ontology.org/query_tree?search=True&node={}'.format(ontology_id)  # NOQA
            r = requests.get(url, timeout=20)
            if not r.status_code == 500:
                rsp = r.json()
                return get_hierarchy_family(get_hierarchy(rsp[0], []))['text']
        (ontology, k) = ontology_id.split(':')
        if not (ontology == 'SNOMEDCT' or
                ontology == 'DOID' or
                ontology == 'RCD' or
                ontology == 'OMIM'):
            k = ontology_id
        url = 'http://data.bioontology.org/ontologies/{}/classes/{}/ancestors?apikey={}'.format(ontology, k, API_KEY)  # NOQA
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            classes = r.json()
            if len(classes) > 0:
                return r.json()[0]['prefLabel']
        return None
    except Exception as e:
        logging.exception(e)
        logging.error('get_family {} {} {}'.format(url, r, e))
        return None


def get_hierarchy(node, hierarchy_list):
    if (
        node.get('iconCls', '') == 'search-select-icon' or
        node.get('expanded', False)
    ):
        hierarchy_list.append({'text': node['text'], 'id': node['id']})
        for n in node.get('children', []):
            get_hierarchy(n, hierarchy_list)
    return hierarchy_list


def print_hierarchy(hierarchy_list, indent=0):
    for node in hierarchy_list:
        print ''.ljust(indent), node['text'], node['id']
        indent = indent + 2


def get_hierarchy_family(_a):
    midpoint = int(len(_a)/2) + 1
    return _a[midpoint]


def normalize(name):
    try:
        name = name.encode('utf8')
    except Exception as e:
        pass
    try:
        diseases = []
        name = project_lookup(name)
        if name:
            # find in ebi
            normalized_diseases = normalize_ebi(name)
            if len(normalized_diseases) > 0:
                diseases = diseases + normalized_diseases
            else:
                names = re.split("[\,;]+", name)
                for name_part in names:
                    name_part = project_lookup(name_part)
                    logging.debug("name_part {}".format(name_part))
                    normalized_diseases = normalize_ebi(name_part)
                    # if we had to break this apart to find a hit,
                    # add the original name back
                    for normalized_disease in normalized_diseases:
                        normalized_disease['label'] = name
                    diseases = diseases + normalized_diseases
            if len(diseases) == 0:
                diseases = normalize_bioontology(name)

        return diseases
    except Exception as e:
        logging.warning("Could not normalize {}".format(name))
        # raise e
        return []


def normalize_multi(phenotypes):
    diseases = []
    for pheno in phenotypes:
        disease = normalize(pheno['description'])
        if len(disease) != 0:
            phenotype = {
                'id': disease[0]['ontology_term'],
                'term': disease[0]['label'],
                'source': disease[0]['source'],
                'description': disease[0]['label']
            }
            if 'family' in disease[0]:
                phenotype['family'] = disease[0]['family']
            diseases.append(phenotype)
    return diseases


def normalize_feature_association(feature_association):
    """ given the 'final' g2p feature_association,
    update it with normalized diseases """
    # nothing to read?, return
    association = feature_association['association']
    if 'phenotypes' not in association:
        return
    diseases = normalize_multi(association['phenotypes'])
    if len(diseases) == 0:
        feature_association['dev_tags'].append('no-doid')
        for i in range(len(association['phenotypes'])):
            association['phenotypes'][i]['family'] = 'Uncategorized-PHN'
        return
    association['phenotypes'] = diseases
    return


def project_lookup(name):
    disease = disease_alias.get(name.lower())
    if not disease == name and disease:
        logging.debug('renamed {} to {}'.format(name, disease))
    if not disease:
        disease = name
    return disease
