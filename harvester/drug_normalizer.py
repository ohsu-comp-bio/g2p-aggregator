import requests
import re
import logging
import pydash
# cache responses
# import requests_cache
# requests_cache.install_cache('harvester')

"""
curl 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/Bayer/synonyms/JSON' | jq '.InformationList.Information[] | [.CID, .Synonym[0]] '
"""  # NOQA

NOFINDS = []

NOFINDS_PUBCHEM_SUBSTANCE = []
NOFINDS_PUBCHEM = []
NOFINDS_BIOTHINGS = []


def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def _decompose(name):
    """given a name, split into an array of searchable terms"""
    name_parts = re.split('\W+', name)
    no_punct = ' '.join(name_parts).strip()
    name_parts = no_punct.split()
    pairs = [' '.join(c) for c in _chunks(name_parts, 2)]
    logging.debug('pairs {} {} >{}<'.format(pairs, len(name_parts), no_punct))
    if len(name_parts) == 1:
        logging.debug('returning [no_punct] {}'.format([no_punct]))
        return [no_punct]
    if name_parts == no_punct.split():
        logging.debug('returning [name_parts] {}'.format(name_parts))
        return name_parts
    if [no_punct] == pairs:
        logging.debug('returning pairs + name_parts {}'.format(pairs + name_parts))
        return pairs + name_parts
    logging.debug('returning [no_punct] + pairs + name_parts {}'.format([no_punct] + pairs + name_parts))
    return [no_punct] + pairs + name_parts


def normalize_pubchem_substance(name):
    """ call pubchem and retrieve compound_id and most common synonym
        see https://pubchem.ncbi.nlm.nih.gov/rdf/#_Toc421254632
    """
    if name in NOFINDS_PUBCHEM_SUBSTANCE:
        logging.info("NOFINDS_PUBCHEM_SUBSTANCE {}".format(name))
        return []
    name_parts = _decompose(name)
    compounds = []
    try:
        for name_part in name_parts:
            if len(name_part) < 3:
                continue
            if name_part in NOFINDS_PUBCHEM_SUBSTANCE:
                continue
            url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/name/{}/synonyms/JSON'.format(name_part)  # NOQA
            r = requests.get(url, timeout=60)
            rsp = r.json()
            if 'InformationList' in rsp:
                informationList = r.json()['InformationList']
                information = informationList['Information'][0]
                compounds.append({'ontology_term':
                                  'SID{}'.format(information['SID']),
                                  'synonym': information['Synonym'][0],
                                  'source': 'http://rdf.ncbi.nlm.nih.gov/pubchem/substance'})
            else:
                logging.info("NOFINDS_PUBCHEM_SUBSTANCE {}".format(name_part))
                NOFINDS_PUBCHEM_SUBSTANCE.append(name_part)
        if len(compounds) == 0:
            NOFINDS_PUBCHEM_SUBSTANCE.append(name)
        return compounds
    except Exception as e:
        logging.warning(e)
        return []


def normalize_pubchem(name):
    """ call pubchem and retrieve compound_id and most common synonym
        see https://pubchem.ncbi.nlm.nih.gov/rdf/#_Toc421254632
    """
    if name in NOFINDS_PUBCHEM:
        logging.info("NOFINDS_PUBCHEM {}".format(name))
        return []
    name_parts = _decompose(name)
    compounds = []
    for name_part in name_parts:
        if len(name_part) < 3:
            continue
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/synonyms/JSON'.format(name_part)  # NOQA
        r = requests.get(url, timeout=60)
        rsp = r.json()
        if 'InformationList' in rsp:
            informationList = r.json()['InformationList']
            information = informationList['Information'][0]
            compounds.append({'ontology_term':
                              'CID{}'.format(information['CID']),
                              'source': 'http://rdf.ncbi.nlm.nih.gov/pubchem/compound',
                              'synonym': information['Synonym'][0]})
    if len(compounds) == 0:
        NOFINDS_PUBCHEM.append(name)
    return compounds


def normalize_biothings(name):
    """
     curl 'http://c.biothings.io/v1/query?q=chembl.molecule_synonyms.synonyms:aspirin&fields=pubchem.cid,chembl.molecule_synonyms,chembl.molecule_chembl_id,chebi.chebi_id' | jq .
    """  # NOQA
    try:
        if name in NOFINDS_BIOTHINGS:
            logging.info("NOFINDS_BIOTHINGS {}".format(name))
            return []
        name_parts = _decompose(name)
        logging.debug(name_parts)
        compounds = []
        for name_part in name_parts:
            if len(name_part) < 3:
                continue
            fields = 'fields=pubchem.cid,chebi.chebi_id'\
                ',chembl.molecule_chembl_id'\
                ',chembl.molecule_synonyms,drugbank.pharmacology.toxicity,' \
                'drugbank.products.approved,drugbank.products.country,' \
                'drugbank.taxonomy.class,drugbank.taxonomy.direct-parent,' \
                'drugbank.taxonomy.kingdom,drugbank.taxonomy.subclass,' \
                'drugbank.taxonomy.superclass,' \
                'chembl.usan_stem_definition'
            url = 'http://c.biothings.io/v1/query?q=chembl.pref_name:{}&{}'.format(name_part, fields)  # NOQA
            logging.debug(url)
            r = requests.get(url, timeout=60)
            rsp = r.json()
            hits = rsp['hits']
            logging.debug('len(hits) {}'.format(len(hits)))
            if len(hits) == 0:
                url = 'http://c.biothings.io/v1/query?q=chembl.molecule_synonyms.synonyms:{}&{}'.format(name_part, fields)  # NOQA
                logging.debug(url)
                r = requests.get(url, timeout=60)
                rsp = r.json()
                logging.debug(rsp)

            if 'hits' in rsp:
                hits = rsp['hits']
                logging.debug('len(hits) {}'.format(len(hits)))
                if len(hits) == 0:
                    continue
                # sort to get best hit
                hits = sorted(hits, key=lambda k: k['_score'], reverse=True)
                hit = hits[0]
                if 'pubchem' not in hit and 'chebi' not in hit and 'chembl' not in hit:  # NOQA
                    logging.warning('no pubchem or chebi or chembl for {}'
                                    .format(name))
                    continue
                # The higher the _score, the more relevant the document.
                if hit['_score'] < 8.8:
                    logging.debug(
                        'discarded, score too low {}'.format(hit['_score'])
                        )
                    continue

                chembl = hit['chembl']
                synonym_fda = synonym_usan = synonym_inn = None
                if 'molecule_synonyms' in chembl:
                    molecule_synonyms = chembl['molecule_synonyms']
                    if type(molecule_synonyms) is list:
                        for molecule_synonym in molecule_synonyms:
                            if molecule_synonym['syn_type'] == 'FDA':
                                synonym_fda = molecule_synonym['synonyms'].encode('utf8')
                            if molecule_synonym['syn_type'] == 'USAN':
                                synonym_usan = molecule_synonym['synonyms'].encode('utf8')
                            if molecule_synonym['syn_type'] == 'INN':
                                synonym_inn = molecule_synonym['synonyms'].encode('utf8')
                    else:
                        if molecule_synonyms['syn_type'] == 'FDA':
                            synonym_fda = molecule_synonyms['synonyms'].encode('utf8')
                        if molecule_synonyms['syn_type'] == 'USAN':
                            synonym_usan = molecule_synonyms['synonyms'].encode('utf8')
                        if molecule_synonyms['syn_type'] == 'INN':
                            synonym_inn = molecule_synonyms['synonyms'].encode('utf8')


                toxicity = pydash.get(hit,
                                      'drugbank.pharmacology.toxicity',
                                      None)
                taxonomy = pydash.get(hit,
                                      'drugbank.taxonomy',
                                      None)

                usan_stem = pydash.get(hit,
                                       'chembl.usan_stem_definition',
                                       None)
                approved_countries = []
                products = pydash.get(hit, 'drugbank.products', [])
                if type(products) is list:
                    for product in products:
                        if product['approved']:
                            approved_countries.append(product['country'])
                else:
                    product = products
                    if product['approved']:
                        approved_countries.append(product['country'])

                approved_countries = list(set(approved_countries))

                ontology_term = None
                source = None
                if 'pubchem' in hit:
                    ontology_term = '{}'.format(hit['pubchem']['cid'])
                    source = 'http://rdf.ncbi.nlm.nih.gov/pubchem/compound'
                if not ontology_term and 'chebi' in hit:
                    ontology_term = hit['chebi']['chebi_id']
                    source = 'http://purl.obolibrary.org/obo/chebi'
                if not ontology_term and 'chembl' in hit:
                    ontology_term = hit['chembl']['molecule_chembl_id']
                    source = 'http://rdf.ebi.ac.uk/terms/chembl'

                compound = {'ontology_term': ontology_term,
                            'synonym': synonym_fda or synonym_usan or
                            synonym_inn or name_part,
                            'source': source
                            }
                if toxicity:
                    compound['toxicity'] = toxicity
                if taxonomy:
                    compound['taxonomy'] = taxonomy
                if len(approved_countries) > 0:
                    compound['approved_countries'] = approved_countries
                if usan_stem:
                    compound['usan_stem'] = usan_stem
                compounds.append(compound)
        if len(compounds) == 0:
            NOFINDS_BIOTHINGS.append(name)
        return compounds
    except Exception as e:
        logging.warning(e)
        return []


def normalize_chembl(name):
    """ chembl """
    name_parts = _decompose(name)
    compounds = []
    for name_part in name_parts:
        if len(name_part) < 3:
            continue
        try:
            url = 'https://www.ebi.ac.uk/chembl/api/data/chembl_id_lookup/search?q={}'.format(name_part)  # NOQA
            r = requests.get(url,
                             headers={'Accept': 'application/json'},
                             timeout=5)
            rsp = r.json()
            if 'chembl_id_lookups' in rsp and len(rsp['chembl_id_lookups']) > 0:
                lookup = rsp['chembl_id_lookups'][0]
                url = 'https://www.ebi.ac.uk{}'.format(lookup['resource_url'])
                data = requests.get(url,
                                    headers={'Accept': 'application/json'},
                                    timeout=5).json()
                if 'molecule_synonyms' not in data:
                    continue
                molecule_synonyms = data['molecule_synonyms']
                synonym_fda = synonym_usan = synonym_inn = None
                for molecule_synonym in molecule_synonyms:
                    if molecule_synonym['syn_type'] == 'FDA':
                        synonym_fda = molecule_synonym['synonyms'].encode('utf8')
                    if molecule_synonym['syn_type'] == 'USAN':
                        synonym_usan = molecule_synonym['synonyms'].encode('utf8')
                    if molecule_synonym['syn_type'] == 'INN':
                        synonym_inn = molecule_synonym['synonyms'].encode('utf8')
                if not (synonym_fda or synonym_usan or synonym_inn):
                    continue
                compounds.append({'ontology_term':
                                  '{}'.format(lookup['chembl_id']),
                                  'synonym': synonym_fda or synonym_usan or
                                  synonym_inn,
                                  'source': 'http://rdf.ebi.ac.uk/terms/chembl' })
        except Exception as e:
            pass
    return compounds


def normalize(name):
    """ given a drug name """

    if name == "N/A":
        return []
    if name in NOFINDS:
        return []
    try:
        name = name.encode('utf8')
    except Exception as e:
        pass
    drugs = normalize_biothings(name)
    if len(drugs) == 0:
        # print 'normalize_pubchem', name
        drugs = normalize_pubchem(name)
    if len(drugs) == 0:
        # print 'normalize_pubchem_substance', name
        drugs = normalize_pubchem_substance(name)
    if len(drugs) == 0:
        # print 'normalize_chembl'
        drugs = normalize_chembl(name)
    if len(drugs) == 0:
        logging.warning('normalize_drugs NOFIND {}'
                        .format(name))
        # skip next time
        NOFINDS.append(name)
    return drugs


def normalize_feature_association(feature_association):
    """ given the 'final' g2p feature_association,
    update it with normalized drugs """
    # nothing to read?, return
    association = feature_association['association']
    if ('environmentalContexts' not in association or
            association['environmentalContexts'] == []):
        # skip if they have no drugs
        # logging.warning('normalize_drugs NODRUGS {}'
        #                 .format(feature_association['source']))
        return
    compounds = []
    for ctx in association['environmentalContexts']:
        ctx_drugs = normalize(ctx['description'])
        if len(ctx_drugs) > 0:
            compounds.extend(ctx_drugs)
        else:
            ctx['usan_stem'] = 'Uncategorized-ENV'
    # nothing found?, return
    if len(compounds) == 0:
        feature_association['dev_tags'].append('no-pubchem')
        return
    environmental_contexts = []
    drug_labels = []
    for compound in compounds:
        ctx = {
            'id': compound['ontology_term'],
            'term': compound['synonym'],
            'description': compound['synonym'],
            'source': compound['source']
        }
        if 'toxicity' in compound:
            ctx['toxicity'] = compound['toxicity']
        if 'approved_countries' in compound:
            ctx['approved_countries'] = compound['approved_countries']
        if 'taxonomy' in compound:
            ctx['taxonomy'] = compound['taxonomy']
        if 'usan_stem' in compound:
            ctx['usan_stem'] = compound['usan_stem']
        environmental_contexts.append(ctx)
        if (compound['synonym']):
            drug_labels.append(compound['synonym'])
    association['environmentalContexts'] = environmental_contexts

    if len(drug_labels) > 0:
        association['drug_labels'] = ','.join(drug_labels)
