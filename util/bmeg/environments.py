#!/usr/bin/python
# -*- coding: utf-8 -*-
import genes

# keep track of what we've already exported
exported = []


def environment_gid(f):
    """ given a environment, hash it"""
    """
 "source": "http://rdf.ncbi.nlm.nih.gov/pubchem/compound",
  "term": "AT13148",
  "id": "CID24905401",
  "description": "AT13148"
    """
    a = []
    gid_name = ''
    # source should be [CID, SID, CHEBI, CHEMBL, unknown]
    # source should be [PUBCHEM, CHEBI, CHEMBL, unknown]
    # TODO - add source to output
    source = None
    if 'source' in f:
        if 'pubchem' in f['source']:
            source = 'PUBCHEM'
        if 'chebi' in f['source']:
            source = 'CHEBI'
        if 'chembl' in f['source']:
            source = 'CHEMBL'
        a.append(f.get('id'))
    else:
        a = []
        description = f.get('description', None)
        if not description:
            description = 'None'
        a.append(description)
        source = 'UNKNOWN'
    return (':'.join(a), source)


def normalize(hit):
    """ returns a tuple of (hit, environments), where hit has been modified to
    normalize hit.environments[] and the  environments[] array
    contains environments observed in this hit that have not yet been returned
    """
    environments = {}
    remove_from_hit = []
    already_exported = []
    # hash each environment
    if 'environmentalContexts' in hit['association']:
        for environment in hit['association']['environmentalContexts']:
            (gid, source) = environment_gid(environment)
            name = environment['description']
            if 'term' in environment:
                name = environment['term']
            environments[gid] = {'id': gid,
                                 'name': name,
                                 'source': [source]
                                 }
        hit['association']['environmentalContexts'] = list(environments.keys())
        for k in environments.keys():
            if k in exported:
                del environments[k]
        exported.extend(environments.keys())
    return (hit, environments)


if __name__ == '__main__':
    """ testing """
    COMPLEX_ENV = \
        {
          "term": "PONATINIB",
          "description": "PONATINIB",
          "taxonomy": {
            "kingdom": "Chemical entities",
            "direct-parent": "Benzanilides",
            "class": "Benzenoids",
            "subclass": "Benzene and substituted derivatives",
            "superclass": "Organic compounds"
          },
          "source": "http://rdf.ncbi.nlm.nih.gov/pubchem/compound",
          "usan_stem": "tyrosine kinase inhibitors",
          "toxicity": "The most common non-hematologic adverse reactions (\u2265 20%) were hypertension, rash, abdominal pain, fatigue, headache, dry skin, constipation, arthralgia, nausea, and pyrexia. Hematologic adverse reactions included thrombocytopenia, anemia, neutropenia, lymphopenia, and leukopenia.",
          "approved_countries": [
            "Canada",
            "US"
          ],
          "id": "CID24826799"
        }

    SIMPLE_ENV = {
      "description": "944396-07-0"
    }

    simple_rsp = normalize({'association': {'environmentalContexts': [SIMPLE_ENV]}})[1]  # noqa
    assert simple_rsp == {'unknown:944396-07-0': {'id': 'unknown:944396-07-0', 'name': '944396-07-0'}}  # noqa
    complex_rsp = normalize({'association': {'environmentalContexts': [COMPLEX_ENV]}})[1].values()[0]  # noqa
    assert {'id': 'PUBCHEM:CID24826799', 'name': 'PONATINIB'} == complex_rsp  # noqa
    assert {} == normalize({'association': {'environmentalContexts': [SIMPLE_ENV, COMPLEX_ENV]}})[1]  # noqa
