import requests
import urllib


def normalize_ebi(name):
    """ call ebi & retrieve """
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
    r = requests.get(url)
    rsp = r.json()
    if 'response' not in rsp:
        return []
    response = rsp['response']
    numFound = response['numFound']
    if numFound == 0:
        return []
    doc = response['docs'][0]
    return [{'ontology_term': doc['obo_id'].encode('utf8'),
             'label': doc['label'].encode('utf8')}]


def normalize(name):
    try:
        name = name.encode('utf8')
    except Exception as e:
        pass
    return normalize_ebi(name)


def normalize_feature_association(feature_association):
    """ given the 'final' g2p feature_association,
    update it with normalized diseases """
    # nothing to read?, return
    association = feature_association['association']
    if 'phenotype' not in association:
        return
    diseases = normalize(association['phenotype']['description'])
    if len(diseases) == 0:
        feature_association['dev-tags'].append('no-doid')
        return
    # TODO we are only looking for exact match of one disease right now
    association['phenotype']['type'] = {
        'id': diseases[0]['ontology_term'],
        'term': diseases[0]['label']
    }
    association['phenotype']['description'] = diseases[0]['label']
