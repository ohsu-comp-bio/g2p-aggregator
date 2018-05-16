#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os

# load gene names
# ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/json/non_alt_loci_set.json
GENES = {}
ALIASES = {}
DATA_DIR = os.environ.get('HARVESTER_DATA', '../data')


# trim payload, we only need symbol and ensembl
data = json.load(open('{}/non_alt_loci_set.json'.format(DATA_DIR)))
for doc in data['response']['docs']:
    gene = {
        'symbol': doc['symbol'],
        'ensembl_gene_id': doc.get('ensembl_gene_id', None),
        'entrez_id': doc.get('entrez_id', None)
        }
    GENES[doc['symbol']] = gene
    if gene['ensembl_gene_id']:
        ALIASES[gene['ensembl_gene_id']] = gene
    if gene['entrez_id']:
        ALIASES[gene['entrez_id']] = gene
    for alias in doc.get('alias_symbol', []):
        ALIASES[alias] = gene
    for prev in doc.get('prev_symbol', []):
        ALIASES[prev] = gene
data = None


def get_gene(identifier):
    """ return gene for identifier """
    for store in [GENES, ALIASES]:
        gene = store.get(identifier, None)
        if gene:
            return gene
    return None
