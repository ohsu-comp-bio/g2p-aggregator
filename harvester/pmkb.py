from __future__ import print_function
import sys

from lxml import html
from lxml import etree
import requests
from inflection import parameterize, underscore
import json
import evidence_label as el
import evidence_direction as ed
import mutation_type as mut


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def _include(interpretation, genes):
    """ should this interpretation be included ? """
    if not genes or len(genes) == 0:
        return True
    if interpretation['gene']['name'] in genes:
        return True
    return False


def harvest(genes=None):
    """ get data from pmkb """
    url = 'https://ga4gh:g2p@pmkb.weill.cornell.edu/api/interpretations'
    response = requests.get(url)
    summaries = json.loads(response.text)
    for interpretation in summaries['interpretations']:
        if _include(interpretation, genes):
            url = 'https://ga4gh:g2p@pmkb.weill.cornell.edu/api/interpretations/{}'.format(interpretation['id'])  # NOQA
            response = requests.get(url)
            detail = json.loads(response.text)
            yield detail['interpretation']


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
                feature['start'] = start
                feature['end'] = stop
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

                gene = variant['gene']['name']

                association = {}

                # association['evidence_label'] = interpretation['tier']
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


def _test_simple():
    for gene in get_gene_symbols(['BRAF']):
        therapies = get_gene_therapies(gene)
        _eprint(len(therapies))
        assert len(therapies) == 26
        for therapy_url in therapies:
            evidence = get_therapy(therapy_url)
            _eprint(evidence.keys())
            break


def _test_harvest():
    for feature_association in harvest_and_convert(None):
        _eprint(feature_association)
        break


if __name__ == '__main__':
    import requests_cache
    # cache responses
    requests_cache.install_cache('harvester')
    _test_harvest()
