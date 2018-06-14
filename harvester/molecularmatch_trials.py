
import requests
import json
import os
import evidence_label as el
import evidence_direction as ed
import logging
from warnings import warn
import sys
import time

DEFAULT_GENES = ['*']
TRIAL_IDS = []


def get_evidence(gene_ids=None):
    """ load from remote api, ignores genes - returns all CANCER trials """
    # override with data from file if it exists
    if os.path.isfile('molecularmatch_trials.json'):
        for evidence in get_evidence_from_file('molecularmatch_trials.json'):
            yield evidence
        return
    # otherwise, get data from remote api
    apiKey = os.environ.get('MOLECULAR_MATCH_API_KEY')
    if not apiKey:
        raise ValueError('Please set MOLECULAR_MATCH_API_KEY in environment')

    if not gene_ids:
        gene_ids = DEFAULT_GENES

    count = 0
    start = int(os.getenv('MM_TRIALS_START', 0))
    end = int(os.getenv('MM_TRIALS_END', sys.maxint))
    limit = 20
    filters = [{'facet': 'CONDITION', 'term': 'CANCER'}]
    resourceURLs = {
        "trials": "/v2/trial/search"
    }
    mmService = "http://api.molecularmatch.com"
    apiKey = os.environ.get('MOLECULAR_MATCH_API_KEY')
    url = mmService + resourceURLs["trials"]

    while start >= 0:
        payload = {
            'apiKey': apiKey,
            'limit': limit,
            'start': start,
            'filters': json.dumps(filters)
        }
        try:
            # time.sleep(2)  # rate limit
            logging.info('%s %s', url, json.dumps(payload))
            r = requests.post(url, data=payload, timeout=120)
            assertions = r.json()
            if 'page' not in assertions:
                logging.info(assertions)
            logging.info(
                "page {} of {}. total {} count {}".format(
                    assertions['page'],
                    assertions['totalPages'],
                    assertions['total'],
                    count
                    )
            )
            # filter those drugs, only those with diseases
            for hit in assertions['rows']:
                count += 1
                yield hit
            if assertions['total'] == 0:
                start = -1
                continue
            else:
                start = start + limit
            if start > end:
                logging.info("reached end {}".format(end))
                start = -1
        except requests.exceptions.ConnectionError as ce:
            logging.error(
                "molecularmatch ConnectionError, retrying. fetching {}"
                .format(gene),
            )
        except Exception as e:
            logging.error(
                "molecularmatch error fetching {}".format(gene),
                exc_info=1
            )
            start = -1


def get_evidence_from_file(filepath):
    """ read raw mm data from file """
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            evidence = json.loads(line)
            yield evidence["molecularmatch_trials"]
            line = fp.readline()


def get_evidence_from_file(filepath):
    """ read raw mm data from file """
    with open(filepath) as fp:
        line = fp.readline()
        while line:
            evidence = json.loads(line)
            yield evidence["molecularmatch_trials"]
            line = fp.readline()


def convert(evidence):
    """

    """
    # print '****', evidence['id'], evidence['phase']
    # print '  ', evidence['title']
    evidence_tags = [{'facet': 'ID', 'term': evidence['id']},
                     {'facet': 'PHASE', 'term': evidence['phase']},
                     {'facet': 'TITLE', 'term': evidence['title']}]
    for t in evidence['tags']:
        if t.get("filterType", None) == "include" and \
           t.get("suppress", True) is False:
            evidence_tags.append(t)

    has_drug = False
    has_condition = False
    has_gene = False
    has_mutation = False
    for t in evidence_tags:
        if t['facet'] == 'CONDITION':
            has_condition = True
        if t['facet'] == 'DRUG':
            has_drug = True
        if t['facet'] == 'GENE':
            has_gene = True
        if t['facet'] == 'MUTATION':
            has_mutation = True
    if has_drug and has_condition and has_gene:
        feature_objs = []

        genes = set([])
        features = set([])
        drugs = set([])
        conditions = []
        priority_phenotype = None

        for t in evidence_tags:
            if t['facet'] == 'GENE':
                genes.add(t['term'])
            if t['facet'] == 'MUTATION':
                features.add(t['term'])
                feature_objs.append({'description': t['term']})
            if t['facet'] == 'DRUG':
                drugs.add(t['term'])
            if t['facet'] == 'CONDITION':
                conditions.append({ 'description' : t['term'] })

        genes = list(genes)
        features = list(features)
        drugs = list(drugs)

        association = {}
        association['phenotypes'] = conditions
        #association['phenotype'] = {'description': condition}
        association['description'] = evidence['title']
        association['environmentalContexts'] = []
        for drug in drugs:
            association['environmentalContexts'].append(
                {'description': drug})
        association['evidence'] = [{
            "evidenceType": {
                "sourceName": "molecularmatch_trials"
            },
            'description': evidence['title'],
            'info': {
                'publications': [
                    'https://clinicaltrials.gov/ct2/show/{}'
                    .format(evidence['id'])]
            }
        }]
        # add summary fields for Display
        association = el.evidence_label(evidence['phase'],
                                        association, na=False)
        feature_association = {
                               'genes': genes,
                               'feature_names': features,
                               'features': feature_objs,
                               'association': association,
                               'source': 'molecularmatch_trials',
                               'molecularmatch_trials': evidence
                               }
        yield feature_association


def harvest(genes):
    """ get data from mm """
    for evidence in get_evidence(genes):
        yield evidence


def harvest_and_convert(genes):
    """ get data from mm, convert it to ga4gh and return via yield """
    for evidence in harvest(genes):
            for feature_association in convert(evidence):
                yield feature_association


def _test():
    # gene_ids = ["CCND1", "CDKN2A", "CHEK1", "DDR2", "FGF19", "FGF3",
    #  "FGF4", "FGFR1", "MDM4", "PALB2", "RAD51D"]
    gene_ids = None
    for feature_association in harvest_and_convert(gene_ids):
        print feature_association.keys()
        print feature_association['features']
        # print json.dumps(feature_association, indent=2)
        break

    # for evidence in harvest(gene_ids):
    #     #print evidence['narrative']
    #     print json.dumps(evidence, indent=2)
    #     break

if __name__ == '__main__':
    import yaml
    import logging.config
    path = 'logging.yml'
    with open(path) as f:
        config = yaml.load(f)
    logging.config.dictConfig(config)
    _test()
