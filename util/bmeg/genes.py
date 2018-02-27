#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import logging
logger = logging.getLogger(__name__)
EXPORTED = []

# load gene names see https://www.genenames.org/cgi-bin/download
GENE_NAMES = {}


class Gene(object):
    """ corrsponds with
    https://github.com/biostream/schemas/blob/g2p/proto/bmeg/genome.proto#L41
    """
    def __init__(self, row):
        self.description = row[0]
        self.symbol = row[1]
        # self.status = row[2]
        # self.entrez = row[3]
        self.id = row[4]

with open('genenames.tsv', 'rb') as tsvin:
    tsvin = csv.reader(tsvin, delimiter='\t')
    for row in tsvin:
        gene_name = Gene(row)
        GENE_NAMES[gene_name.symbol] = gene_name


def gene_lookup(gene):
    lookup = gene.replace('Wild-Type', '').strip()
    gene_name = GENE_NAMES.get(lookup, None)
    # if gene_name and '' in gene_name.id:
    #     print '!gene_lookup', gene_name.__dict__
    #     exit(1)
    return gene_name


def normalize(hit):
    _genes = {}
    # lookup ensembl for each gene
    for gene in hit['genes']:
        gene_name = gene_lookup(gene)
        if gene_name:
            if not gene_name.id:
                logger.warning('no ensembl for {} {}'.format(gene,
                                                             gene_name.__dict__))  # noqa
                _genes['{}'.format(gene)] = gene_name.__dict__
            else:
                _genes['{}'.format(gene_name.id)] = gene_name.__dict__
        else:
            logger.error('no genename for {}'.format(gene))
            _genes['{}'.format(gene)] = {}

    hit['genes'] = list([k for k in _genes.keys()])
    for k in _genes.keys():
        if k in EXPORTED:
            del _genes[k]
    EXPORTED.extend([k for k in _genes.keys()])
    return (hit, _genes)


if __name__ == '__main__':
    # testing
    kit = normalize({'genes': ['KIT']})
    # print kit
    assert ({'genes': ['ENSG00000157404']}, {'ENSG00000157404': {'symbol': 'KIT', 'description': 'HGNC:6342', 'id': 'ENSG00000157404'}}) == kit  # noqa
    kit_brca1 = normalize({'genes': ['KIT', 'BRCA1']})
    # print kit_brca1
    assert ({'genes': ['ENSG00000157404', 'ENSG00000012048']}, {'ENSG00000012048': {'symbol': 'BRCA1', 'description': 'HGNC:1100', 'id': 'ENSG00000012048'}}) == kit_brca1  # noqa



    import sys
    # biostream-schema
    from bmeg.clinical_pb2 import *
    from bmeg.cna_pb2 import *
    from bmeg.genome_pb2 import *
    from bmeg.phenotype_pb2 import *
    from bmeg.rna_pb2 import *
    from bmeg.variants_pb2 import *
    from google.protobuf import json_format
    import json
    from google.protobuf.json_format import MessageToJson, MessageToDict
    def _writePB(cls, obj, file):
        pb_obj = eval('{}()'.format(cls))
        o = json_format.Parse(json.dumps(obj), pb_obj, ignore_unknown_fields=False)
        data = MessageToDict(o)
        file.write(json.dumps(data, separators=(',', ':')))
        file.write('\n')


    _writePB('G2PAssociation', kit[0], sys.stdout)
