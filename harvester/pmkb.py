from __future__ import print_function
import sys

import requests
from inflection import parameterize, underscore
import json
import evidence_label as el
import evidence_direction as ed
import mutation_type as mut


def harvest(genes=None):
    with open("../data/pmkb_interpretations.json", "r") as ins:
        for line in ins:
            interpretations = json.loads(line)['interpretations']
            for interpretation in interpretations:
                yield interpretation


def convert(interpretation):
    """create feature_association from pmkb evidence"""
    for variant in interpretation['variants']:
        if 'coordinates' in variant:
            # '7:140453135-140453136'
            # '3:41266097-41266099, 3:41266100-41266102, 3:41266103-41266105, 3:41266106-41266108, 3:41266109-41266111, 3:41266112-41266114, 3:41266124-41266126, 3:41266136-41266138'  # NOQA
            s = variant['coordinates']
            if not s:
                continue
            coordinates = s.replace(' ', '').split(',')
            for coordinate in coordinates:
                feature = {}
                feature['geneSymbol'] = variant['gene']['name']
                feature['name'] = variant['name']
                a = coordinate.split(':')
                chromosome = a[0]
                start, stop = a[1].split('-')
                feature['start'] = int(start)
                feature['end'] = int(stop)
                feature['chromosome'] = str(chromosome)
                feature['referenceName'] = 'GRCh37/hg19'
                feature['biomarker_type'] = mut.norm_biomarker(
                                                variant['variant_type']
                                            )

                attributes = {}
                for key in variant.keys():
                    if key not in ['coordinates', 'name', 'gene']:
                        attributes[key] = {'string_value': variant[key]}
                feature['attributes'] = attributes

                # TODO - replace w/ biocommons/hgvs ?
                if 'dna_change' in variant:
                    dna_change = variant['dna_change']
                    if dna_change and '>' in dna_change:
                        prefix, alt = dna_change.split('>')
                        ref = prefix[-len(alt):]
                        if len(ref) > 0 and len(alt) > 0:
                            feature['ref'] = ref
                            feature['alt'] = alt

                gene = variant['gene']['name']

                association = {}

                if attributes['amino_acid_change']['string_value']:
                    association['variant_name'] = attributes['amino_acid_change']['string_value']

                # association['evidence_label'] = interpretation['tier']
                association['source_link'] = 'https://pmkb.weill.cornell.edu/variants/{}'.format(variant['id'])
                association = el.evidence_label(str(interpretation['tier']),
                                                association, na=True)
                association = ed.evidence_direction(
                                str(interpretation['tier']),
                                association, na=True)

                association['description'] = interpretation['interpretation']
                # TODO pmkb does not break out drug !?!?
                # association['environmentalContexts'] = []

                for tumor in interpretation['tumors']:
                    association['phenotype'] = {
                        'description': tumor['name']
                    }
                    association['drug_labels'] = 'NA'
                    association['evidence'] = [{
                        "evidenceType": {
                            "sourceName": "pmkb"
                        },
                        'description': str(interpretation['tier']),
                        'info': {
                            'publications': [
                                'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(c['pmid']) for c in interpretation['citations']  # NOQA
                            ]
                        }
                    }]
                    # add summary fields for Display
                    if len(interpretation['citations']) > 0:
                        association['publication_url'] = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(interpretation['citations'][0]['pmid'])  # NOQA
                    feature_association = {'genes': [gene],
                                           'features': [feature],
                                           'feature_names':
                                           '{} {}'.format(
                                                feature["geneSymbol"],
                                                feature["name"]
                                            ),
                                           'association': association,
                                           'source': 'pmkb',
                                           'pmkb': {
                                            'variant': variant,
                                            'tumor': tumor,
                                            'tissues':
                                            interpretation['tissues']
                                           }}
                    yield feature_association


def harvest_and_convert(genes):
    """ get data from pmkb, convert it to ga4gh and return via yield """
    for evidence in harvest(genes):
        # print "harvester_yield {}".format(evidence.keys())
        for feature_association in convert(evidence):
            # print "pmkb convert_yield {}".format(feature_association.keys())
            yield feature_association
