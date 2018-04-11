#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

# load gene names
# ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/json/non_alt_loci_set.json
GENES = {}
ALIASES = {}

# trim payload, we only need symbol and ensembl
data = json.load(open('../data/non_alt_loci_set.json'))
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


def get_genes(identifier):
    """ return gene for identifier """
    for store in [GENES, ALIASES]:
        genes = store.get(identifier, None)
        if genes:
            return genes
    return None


def normalize_feature_association(feature_association):
    """ add gene_identifiers array to feature_association """
    gene_identifiers = []
    for gene_symbol in feature_association['genes']:
        genes = get_genes(gene_symbol)
        if (genes):
            gene_identifiers.extend(genes)
    feature_association['gene_identifiers'] = gene_identifiers
