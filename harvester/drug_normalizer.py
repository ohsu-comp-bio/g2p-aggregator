import requests

"""
curl 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/Bayer/synonyms/JSON' | jq '.InformationList.Information[] | [.CID, .Synonym[0]] '
"""  # NOQA
# TODO - how to deal with misc names?
# e.g. "Everolimus (MTOR inhibitor)" "Trametinib + Dabrafenib"
#      "Dasatinib (BCR-ABL inhibitor 2nd gen)"


def normalize_pubchem_substance(name):
    """ call pubchem and retrieve compound_id and most common synonym
        see https://pubchem.ncbi.nlm.nih.gov/rdf/#_Toc421254632
    """
    name_parts = name.split()  # split on whitespace
    compounds = []
    for name_part in name_parts:
        if len(name_part) < 2:
            continue
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/name/{}/synonyms/JSON'.format(name_part)  # NOQA
        r = requests.get(url)
        rsp = r.json()
        if 'InformationList' in rsp:
            informationList = r.json()['InformationList']
            information = informationList['Information'][0]
            compounds.append({'ontology_term':
                              'substance:SID{}'.format(information['SID']),
                              'synonym': information['Synonym'][0]})
    return compounds


def normalize_pubchem(name):
    """ call pubchem and retrieve compound_id and most common synonym
        see https://pubchem.ncbi.nlm.nih.gov/rdf/#_Toc421254632
    """
    name_parts = name.split()  # split on whitespace
    compounds = []
    for name_part in name_parts:
        if len(name_part) < 2:
            continue
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/synonyms/JSON'.format(name_part)  # NOQA
        r = requests.get(url)
        rsp = r.json()
        if 'InformationList' in rsp:
            informationList = r.json()['InformationList']
            information = informationList['Information'][0]
            compounds.append({'ontology_term':
                              'compound:CID{}'.format(information['CID']),
                              'synonym': information['Synonym'][0]})
    return compounds


def normalize_biothings(name):
    """
     curl 'http://c.biothings.io/v1/query?q=chembl.molecule_synonyms.synonyms:aspirin&fields=pubchem.cid,chembl.molecule_synonyms' | jq .
    """  # NOQA
    name_parts = name.split()  # split on whitespace
    compounds = []
    for name_part in name_parts:
        if len(name_part) < 2:
            continue
        url = 'http://c.biothings.io/v1/query?q=chembl.molecule_synonyms.synonyms:{}&fields=pubchem.cid,chembl.molecule_synonyms'.format(name_part)  # NOQA
        r = requests.get(url)
        rsp = r.json()
        if 'hits' in rsp:
            hits = rsp['hits']
            if len(hits) == 0:
                continue
            hit = hits[0]
            if 'pubchem' not in hit:
                continue
            chembl = hit['chembl']
            molecule_synonyms = chembl['molecule_synonyms']
            synonym_fda = synonym_usan = synonym_inn = None
            for molecule_synonym in molecule_synonyms:
                if molecule_synonym['syn_type'] == 'FDA':
                    synonym_fda = molecule_synonym['synonyms'].encode('utf8')
                if molecule_synonym['syn_type'] == 'USAN':
                    synonym_usan = molecule_synonym['synonyms'].encode('utf8')
                if molecule_synonym['syn_type'] == 'INN':
                    synonym_inn = molecule_synonym['synonyms'].encode('utf8')

            compounds.append({'ontology_term':
                              'compound:{}'.format(hit['pubchem']['cid']),
                              'synonym': synonym_fda or synonym_usan or
                              synonym_inn})
    return compounds


def normalize(name):
    """ given a drug name """
    try:
        name = name.encode('utf8')
    except Exception as e:
        pass
    drugs = normalize_biothings(name)
    if len(drugs) == 0:
        drugs = normalize_pubchem(name)
    if len(drugs) == 0:
        drugs = normalize_pubchem_substance(name)
    return drugs


def normalize_feature_association(feature_association):
    """ given the 'final' g2p feature_association,
    update it with normalized drugs """
    # nothing to read?, return
    association = feature_association['association']
    if 'environmentalContexts' not in association:
        return
    compounds = []
    for ctx in association['environmentalContexts']:
        ctx_drugs = normalize(ctx['description'])
        if len(ctx_drugs) > 0:
            compounds.extend(ctx_drugs)
    # nothing found?, return
    if len(compounds) == 0:
        feature_association['tags'].append('no-pubchem')
        return
    environmental_contexts = []
    for compound in compounds:
        environmental_contexts.append({
            'id': compound['ontology_term'],
            'term': compound['synonym']
        })
    association['environmentalContexts'] = environmental_contexts
