#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import local
import logging
logger = logging.getLogger(__name__)


ASSOCIATION_KEYS = ["description", "evidence",   "gid",  'original',
                    'source', 'features', 'phenotypes', 'environments']


def association_gid(hit):
    """ given an association, hash it"""
    association = hit['association']
    a = []
    empty_count = 0
    gid_name = 'association:'
    for p in ['source', 'phenotypes', 'features',
              'environmentalContexts', 'evidence']:
        a.append(str(association.get(p, '')))
    m = hashlib.md5()
    m.update(':'.join(a))
    return 'association:{}:{}'.format(hit['source'], m.hexdigest())


def normalize(hit):
    """ returns a tuple of (hit, association), where hit association
    has been modified to remove edge keys and gid inserted
    """
    association = hit['association']
    association['gid'] = association_gid(hit)
    # keep edge keys -
    # # remove edge keys
    # for p in ['features', 'phenotype', 'environmentalContexts']:
    #     if p in association:
    #         del association[p]

    # move genes into association
    association['genes'] = list(hit['genes'])
    del hit['genes']

    # format evidence as bmeg friendly
    evidence = association['evidence'][0]
    new_evidence = {
        'evidence_type': {
            'term_id': '{}:{}'.format(evidence['evidenceType']['sourceName'],
                                      evidence['evidenceType'].get('id', ''))},
        'description': evidence['description'],
    }
    if 'info' in evidence and evidence['info']:
        new_evidence['publications'] = evidence['info']['publications']

    for p in ['evidence_label', 'oncogenic', 'evidence_level',
              'response_type']:
        if p in association:
            new_evidence[p] = str(association[p])
    association['evidence'] = [new_evidence]

    # move the document to 'original'
    association['original'] = hit[hit['source']]
    association['source'] = hit['source']
    if 'environmentalContexts' in association:
        association['environments'] = list(
            association['environmentalContexts'])
        del association['environmentalContexts']

    # move FKs from hit to association
    for p in ['features', 'genes']:
        if p in hit:
            association[p] = list(hit[p])
            del hit[p]
    # clean up any 'features' that are in fact only genes
    if 'features' in association:
        if 'genes' not in association:
            association['genes'] = []
        association['genes'].extend(
            [f for f in association['features'] if f.startswith('gene:')])
        association['features'] = \
            [f for f in association['features'] if not f.startswith('gene:')]

    # clean up any misc keys
    for p in association.keys():
        if p not in ASSOCIATION_KEYS:
            del association[p]
            logger.debug('removing {}'.format(p))

    return (hit, association)


if __name__ == '__main__':
    """ testing """
    import json
    expected = set(ASSOCIATION_KEYS)
    for source in ['cgi', 'jax', 'civic', 'oncokb', 'pmkb',
                   'molecularmatch', 'sage', 'jax_trials', 'brca']:

        with open('../elastic/{}.json'.format(source)) as f:
            content = f.readlines()
            for c in content:
                (hit, association) = normalize(json.loads(c))
                actual = set(association.keys())
                assert actual <= expected, \
                    '{}\n  {}\n  {}'.format(source, actual, expected)
                break
