#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
import argparse
import sys

from genes import normalize as genes_normalize
from features import normalize as features_normalize
from environments import normalize as environments_normalize
from phenotypes import normalize as phenotypes_normalize
from association import normalize as association_normalize

files = {}


def _stdin_actions(args):
    """ create a index record from std in """
    count = 0
    for line in sys.stdin:
        count = count + 1
        if count > args.skip and count <= args.limit:
            hit = json.loads(line)
            (hit, genes) = genes_normalize(hit)
            (hit, features) = features_normalize(hit)
            (hit, environments) = environments_normalize(hit)
            (hit, phenotypes) = phenotypes_normalize(hit)
            (hit, association) = association_normalize(hit)
            yield (genes, features, environments, phenotypes, association)


def _open_all(association):
    # genes_path = '{}.Gene.json'.format(association['source'])
    # features_path = '{}.Feature.json'.format(association['source'])
    # environments_path = '{}.Environment.json' \
    #                     .format(association['source'])
    # phenotype_path = '{}.Phenotype.json'.format(association['source'])
    # association_path = '{}.Association.json' \
    #                    .format(association['source'])
    genes_path = 'biostream/biostream/g2p/Gene.json'
    features_path = 'biostream/biostream/g2p/Variant.json'
    environments_path = 'biostream/biostream/g2p/Compound.json'
    phenotype_path = 'biostream/biostream/g2p/Phenotype.json'
    association_path = 'biostream/biostream/g2p/G2PAssociation.json'

    # edge_path = '{}.Association.Edge.json'.format(association['source'])
    for p in [genes_path, features_path, environments_path,
              phenotype_path, association_path]:
        if p not in files:
            files[p] = open(p, 'wb')
    return (genes_path, features_path, environments_path,
            phenotype_path, association_path)


def _close_all():
    for k in files.keys():
        files[k].close()


def _bulk(_tuple):
    """ tuple to json file(s) """
    genes = _tuple[0]  # obj of genes; gid as key
    features = _tuple[1]  # obj of features; gid as key
    environments = _tuple[2]  # obj of environments; gid as key
    phenotypes = _tuple[3]  # obj of phenotypes; gid as key
    association = _tuple[4]  # association object

    # ensure files are open
    (genes_path, features_path, environments_path, phenotypes_path,
     association_path) = _open_all(association)

    association_gid = association['gid']

    # write genes
    for gid in genes.keys():
        # write data
        data = dict(genes[gid])
        data['id'] = gid
        files[genes_path].write(json.dumps(data, separators=(',', ':')))
        files[genes_path].write('\n')

    # write features
    for gid in features.keys():
        #  write data
        data = features[gid]
        if gid.startswith('variant:'):
            data['id'] = gid
            files[features_path].write(json.dumps(data, separators=(',', ':')))
            files[features_path].write('\n')

    # write environments
    for gid in environments.keys():
        data = environments[gid]
        data['id'] = gid
        files[environments_path].write(json.dumps(data,
                                                  separators=(',', ':')))
        files[environments_path].write('\n')

    # write phenotypes
    for gid in phenotypes.keys():
        data = phenotypes[gid]
        data['id'] = gid
        files[phenotypes_path].write(json.dumps(data, separators=(',', ':')))
        files[phenotypes_path].write('\n')

    # write association data
    del association['gid']
    association['id'] = association_gid
    files[association_path].write(json.dumps(association,
                                             separators=(',', ':')))
    files[association_path].write('\n')


def _from_stdin(args):
    """ todo """
    # write to ES
    if not args.dry_run:
        for _tuple in _stdin_actions(args):
            _bulk(_tuple)
    else:
        for d in _stdin_actions(args):
            if args.verbose:
                print json.dumps(d)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--dry_run', '-d',
                           help='dry run',
                           default=False,
                           action='store_true')
    argparser.add_argument("-v", "--verbose", help="increase output verbosity",
                           default=False,
                           action="store_true")
    argparser.add_argument('--skip',
                           default=-1,
                           type=int,
                           help='skip these lines before importing',
                           )
    argparser.add_argument('--limit',
                           default=sys.maxint,
                           type=int,
                           help='limit',
                           )

    args = argparser.parse_args()
    _from_stdin(args)
    _close_all()
