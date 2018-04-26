#!/usr/bin/python

from pathlib import Path
from os.path import exists
import pandas as pd
import json
import requests
import json
from urllib import urlencode, quote_plus
import csv

import cosmic_lookup_table

import evidence_label as el
import evidence_direction as ed
import mutation_type as mut
import glob


def harvest(genes=None):
    path = "../data/smmart/*.maf"

    for filename in glob.glob(path):
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            for row in reader:
                # variant = 'variant:GRCh37:{}:{}:{}:{}:{}'.format(row['Chromosome'], row['Start_position'], row['End_position'], row['Reference_Allele'], row['Tumor_Seq_Allele2'])
                yield row


def convert(row):
    # variant = 'variant:GRCh37:{}:{}:{}:{}:{}'.format(row['Chromosome'], row['Start_position'], row['End_position'], row['Reference_Allele'], row['Tumor_Seq_Allele2'])

    feature = {}
    feature['chromosome'] = row['Chromosome']
    feature['start'] = long(row['Start_position'])
    if row['End_position']:
        feature['end'] = long(row['End_position'])
    feature['ref'] = row['Reference_Allele']
    feature['alt'] = row['Tumor_Seq_Allele2']
    feature['referenceName'] = 'GRCh37'
    feature['geneSymbol'] = row['Hugo_Symbol']
    feature['name'] = '{} {}'.format(row['Hugo_Symbol'],
                                     row['Protein_Change'])
    if row.get('Description', None):
        feature['description'] = row.get('Description')
    else:
        feature['description'] = ''
    feature['biomarker_type'] = row['Variant_Classification']
    genes = [row['Hugo_Symbol']]
    features = [feature]
    association = {}
    association['phenotype'] = {
        'description': 'Cancer',
    }

    association['evidence'] = [{
        'description': 'variant from patient MAF file',
    }]
    association['oncogenic'] = 'possibly oncogenic'
    association['evidence_label'] = None
    feature_names = ', '.join(['{}:{}'.format(
                            f["geneSymbol"], f["name"]) for f in features])

    feature_association = {'genes': genes,
                           'features': features,
                           'feature_names': feature_names,
                           'association': association,
                           'source': 'smmart',
                           # 'smmart': row
                           }
    yield feature_association



def harvest_and_convert(genes):
    """ get data from oncokb, convert it to ga4gh and return via yield """
    for gene_data in harvest(genes):
        # print "harvester_yield {}".format(jax_evidence.keys())
        for feature_association in convert(gene_data):
            # print "convert_yield {}".format(feature_association.keys())
            yield feature_association


def _test():
    for feature_association in harvest_and_convert(None):
        print feature_association.keys()
        break

if __name__ == '__main__':
    _test()
