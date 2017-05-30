from __future__ import print_function
import sys

from lxml import html
from lxml import etree
import requests
from inflection import parameterize, underscore
import json
import match

def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_gene_therapies(gene):
    """scrape therapies that apply to gene"""
    url = gene['url']
    page = requests.get(url)
    tree = html.fromstring(page.content)
    xpath_data_links = '//*[@data-link]'
    data_links = tree.xpath(xpath_data_links)
    gene_therapies = []
    for data_link in data_links:
        href = data_link.get('data-link')
        if 'therapies' in href:
            url = 'https://pmkb.weill.cornell.edu{}'.format(href)
            gene_therapies.append(url)
    return gene_therapies


def get_gene_symbols(genes):
    """scrape gene list"""
    url = 'https://pmkb.weill.cornell.edu/genes'
    page = requests.get(url)
    tree = html.fromstring(page.content)
    xpath_tbody_trs = '//*[@id="genetable"]/tbody/tr'
    tbody_trs = tree.xpath(xpath_tbody_trs)
    gene_symbols = []
    if len(tbody_trs) == 0:
        _eprint('no table rows found')
    for tr in tbody_trs:
        url = 'https://pmkb.weill.cornell.edu{}'.format(tr.get('data-link'))
        name = tr[0][0].text
        if genes:
            if name in genes:
                gene_symbols.append({'name': name, 'url': url})
        else:
            gene_symbols.append({'name': name, 'url': url})
    return gene_symbols


def get_variant(path):
    """scrape variants"""
    url = 'https://pmkb.weill.cornell.edu{}'.format(path)
    variant = {'url': url}
    page = requests.get(url)
    tree = html.fromstring(page.content)
    xpath_panel = '//div[@class="panel-body"]'
    panels = tree.xpath(xpath_panel)
    for tr in panels[2][0][0]:
        variant[tr[0].text_content()] = tr[1].text_content()
    return variant


def get_therapy(url):
    """scrape therapy"""
    page = requests.get(url)
    if not page.status_code == 200:
        return None

    tree = html.fromstring(page.content)
    xpath_panel = '//div[@class="panel-body"]'
    panel = tree.xpath(xpath_panel)
    interpretation = panel[2]
    variants = []
    for child in interpretation[0][0][1]:
        if (child.tag == 'span'):
            variant = get_variant(child[0].get('href'))
            variant['name'] = child[0].text_content()
            variants.append(variant)

    tumors = []
    for child in interpretation[0][1][1]:
        if (child.tag == 'span'):
            tumors.append(child[0].text_content())

    tissues = []
    for child in interpretation[0][2][1]:
        if (child.tag == 'span'):
            tissues.append(child[0].text_content())

    tier = interpretation[0][3][1].text_content()

    interpretation_text = interpretation[2][0].text

    citations = []
    for child in interpretation:
        if (child.tag == 'p'):
            citations.append({'text': child[0].text,
                              'url': child[0].get('href')})

    return {
        'variants': variants,
        'tumors': tumors,
        'tissues': tissues,
        'interpretation': interpretation_text,
        'citations': citations,
        'tier': tier,
        'url': url
    }


def harvest(genes=None):
    """ get data from pmkb """
    for gene in get_gene_symbols(genes):
        therapies = get_gene_therapies(gene)
        for therapy_url in therapies:
            evidence = get_therapy(therapy_url)
            yield evidence


def convert(evidence):
    """create feature_association from pmkb evidence,
       clean up pmkb variable names"""
    # cleanup
    for variant in evidence['variants']:
        if 'Genomic Coordinates (GRCh37/hg19)' in variant:
            variant['coordinates'] = \
                variant['Genomic Coordinates (GRCh37/hg19)']
            del variant['Genomic Coordinates (GRCh37/hg19)']
        if 'COSMIC ID' in variant:
            variant['cosmic_id'] = \
                variant['COSMIC ID']
            del variant['COSMIC ID']
        if 'DNA Change (Coding Nucleotide)' in variant:
            variant['coding_nucleotide'] = \
                variant['DNA Change (Coding Nucleotide)']
            del variant['DNA Change (Coding Nucleotide)']
        if 'Amino Acid Change' in variant:
            variant['amino_acid_change'] = \
                variant['Amino Acid Change']
            del variant['Amino Acid Change']
        if 'Transcript ID (GRCh37/hg19)' in variant:
            variant['transcript_id'] = \
                variant['Transcript ID (GRCh37/hg19)']
            del variant['Transcript ID (GRCh37/hg19)']
        if 'Germline/Somatic?' in variant:
            variant['cell_class'] = \
                variant['Germline/Somatic?']
            del variant['Germline/Somatic?']
        if 'Codon(s)' in variant:
            variant['condons'] = \
                variant['Codon(s)']
            del variant['Codon(s)']
        if 'Exon(s)' in variant:
            variant['exons'] = \
                variant['Exon(s)']
            del variant['Exon(s)']

    for variant in evidence['variants']:
        if 'coordinates' in variant:
            # '7:140453135-140453136'
            # '3:41266097-41266099, 3:41266100-41266102, 3:41266103-41266105, 3:41266106-41266108, 3:41266109-41266111, 3:41266112-41266114, 3:41266124-41266126, 3:41266136-41266138'  # NOQA
            s = variant['coordinates']
            coordinates = s.replace(' ', '').split(',')
            for coordinate in coordinates:
                feature = {}
                feature['geneSymbol'] = variant['Gene']
                feature['name'] = variant['name']
                a = coordinate.split(':')
                chromosome = a[0]
                start, stop = a[1].split('-')
                feature['start'] = start
                feature['end'] = stop
                feature['chromosome'] = chromosome
                feature['referenceName'] = 'GRCh37/hg19'
                attributes = {}
                for key in variant.keys():
                    if key not in ['coordinates', 'name', 'Gene']:
                        attributes[key] = {'string_value': variant[key]}
                feature['attributes'] = attributes

                gene = variant['Gene']

                association = {}
                association['description'] = evidence['interpretation']

                # association['evidence_label'] = evidence['tier']
                for item in match.ev_lab:
                    for opt in match.ev_lab[item]:
                        if opt in evidence['interpretation'].lower():
                            association['evidence_label'] = item
                if 'evidence_label' not in association:
                    association['evidence_label'] = 'NA'

                for item in match.res_type:
                    for opt in match.res_type[item]:
                        if opt in evidence['interpretation'].lower():
                            association['response_type'] = item
                if 'response_type' not in association:
                    association['response_type'] = 'NA'

                # TODO pmkb does not break out drug !?!?
                # association['environmentalContexts'] = []
                for tumor in evidence['tumors']:
                    association['phenotype'] = {
                        'description': tumor
                    }

                    association['evidence'] = [{
                        "evidenceType": {
                            "sourceName": "pmkb"
                        },
                        'description': evidence['tier'],
                        'info': {
                            'publications': [
                                [c['url'] for c in evidence['citations']]
                            ]
                        }
                    }]
                    # add summary fields for Display
                    
                    if len(evidence['citations']) > 0:
                        association['publication_url'] = evidence['citations'][0]['url']
                    association['drug_labels'] = 'NA'
                    feature_association = {'gene': gene,
                                           'feature': feature,
                                           'association': association,
                                           'source': 'pmkb',
                                           'pmkb': {
                                            'variant': variant,
                                            'tumor': tumor,
                                            'tissues': evidence['tissues'],
                                            'url': evidence['url']
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
    _test_harvest()
