import csv
import sys
import requests
import json

sys.path.append('.')  # NOQA

from drug_normalizer import normalize


# https://github.com/biostream/gdc-transform/blob/master/tcga_pubchem.map
# https://github.com/biostream/ctdd-transform/blob/master/ctdd_pubchem.table
# https://github.com/biostream/ccle-transform/blob/master/ccle_pubchem.txt
# https://github.com/biostream/gdsc-transform/blob/master/gdsc_pubchem.table

def test_biostream():
    files = ['tests/integration/gdsc_pubchem.table',
             'tests/integration/ccle_pubchem.txt']
    print 'test lookups'
    for f_name in files:
        with open(f_name, 'rb') as tsvin:
            tsvin = csv.reader(tsvin, delimiter='\t')
            for row in tsvin:
                name = row[0]
                id = row[1]
                compounds = normalize(name)
                if len(compounds) > 0:
                    msg = ''
                    if id not in compounds[0]['ontology_term']:
                        msg = 'MISMATCH should be CID{} ?'.format(id)
                    print '{}\t{}\t{}'.format(name, compounds[0]['ontology_term'], msg)
                else:
                    print '{}\t\tNO FIND. should be CID{}'.format(name, id)


def test_biostream_validate():
    files = ['tests/integration/gdsc_pubchem.table',
             'tests/integration/ccle_pubchem.txt']
    print 'test lookups'
    for f_name in files:
        with open(f_name, 'rb') as tsvin:
            tsvin = csv.reader(tsvin, delimiter='\t')
            for row in tsvin:
                name = row[0]
                id = row[1]
                url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/synonyms/TXT'.format(id)
                r = requests.get(url)
                if name.lower() in r.text.lower():
                    msg = ''
                    print '{}\tCID{}\t{}'.format(name, id, 'OK')
                else:
                    print '{}\t{}\tNO FIND at {}'.format(name, id, url)


def test_protograph_transform():
    files = ['tests/integration/gdsc_pubchem.table',
             'tests/integration/ccle_pubchem.txt']
    print 'test lookups'
    for f_name in files:
        with open(f_name, 'rb') as tsvin:
            tsvin = csv.reader(tsvin, delimiter='\t')
            for row in tsvin:
                name = row[0]
                id = row[1]
                url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/synonyms/TXT'.format(id)
                r = requests.get(url)
                if name.lower() in r.text.lower():
                    print json.dumps({"source":["PUBCHEM"], "id": "CID{}".format(id), "name": name})
                else:
                    print json.dumps({"source":["UNKNOWN"], "id": "UNKNOWN:{}".format(name), "name": name})
