import requests

"""
curl 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/Bayer/synonyms/JSON' | jq '.InformationList.Information[] | [.CID, .Synonym[0]] '
"""  # NOQA
# TODO - how to deal with misc names?
# e.g. "Everolimus (MTOR inhibitor)" "Trametinib + Dabrafenib"
#      "Dasatinib (BCR-ABL inhibitor 2nd gen)"


def normalize(name):
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
