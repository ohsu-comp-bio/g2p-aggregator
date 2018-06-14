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
    GENES[doc['symbol']] = [gene]
    if gene['ensembl_gene_id']:
        if gene['ensembl_gene_id'] not in ALIASES:
            ALIASES[gene['ensembl_gene_id']] = []
        ALIASES[gene['ensembl_gene_id']].append(gene)
    if gene['entrez_id']:
        if gene['entrez_id'] not in ALIASES:
            ALIASES[gene['entrez_id']] = []
        ALIASES[gene['entrez_id']].append(gene)
    for alias in doc.get('alias_symbol', []):
        if alias not in ALIASES:
            ALIASES[alias] = []
        ALIASES[alias].append(gene)
    for prev in doc.get('prev_symbol', []):
        if prev not in ALIASES:
            ALIASES[prev] = []
        ALIASES[prev].append(gene)
data = None


def get_gene(identifier):
    """ return gene for identifier """
    for store in [GENES, ALIASES]:
        genes = store.get(identifier, None)
        if genes and len(genes) == 1:
            return genes
        else:
            raise ValueError('gene reference does not exist or refers to multiple genes')

def normalize_feature_association(feature_association):
    """ add gene_identifiers array to feature_association """
    gene_identifiers = []
    for gene_symbol in feature_association['genes']:
        try:
            gene = get_gene(gene_symbol)
        except:
            gene = None
        if (gene):
            gene_identifiers.extend(gene)
    feature_association['gene_identifiers'] = gene_identifiers
