#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

# load gene names
# ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/json/non_alt_loci_set.json
GENES = {}

# trim payload, we only need symbol and ensembl
data = json.load(open('../data/non_alt_loci_set.json'))
for doc in data['response']['docs']:
    GENES[doc['symbol']] = {'ensembl_gene_id': doc.get('ensembl_gene_id', None)}
data = None


def get_gene(symbol):
    """ return gene for symbol """
    return GENES.get(symbol, None)
