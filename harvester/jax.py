
import sys
from lxml import html
from lxml import etree
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from inflection import parameterize, underscore
import json
import logging
import evidence_label as el
import evidence_direction as ed
import mutation_type as mut

import cosmic_lookup_table

LOOKUP_TABLE = None

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# see https://ckb.jax.org/about/curationMethodology


def harvest(genes):
    """ get data from jax """
    for gene_id in _get_gene_ids(genes):
        for jax_evidence in get_evidence([gene_id]):
            yield jax_evidence


def _get_gene_ids(genes):
    """gets json for list of all genes and aliases yield"""
    url = 'https://ckb.jax.org/select2/getSelect2GenesForSearchTerm'
    page = requests.get(url, verify=False)
    gene_ids = []
    gene_infos = page.json()
    if not genes:
        for gene_info in gene_infos:
            yield {'id': gene_info['id'], 'gene': gene_info['geneName']}
    else:
        for gene_info in gene_infos:
            for gene in genes:
                if gene in gene_info['text']:
                    yield {'id': gene_info['id'], 'gene': gene}


def get_evidence(gene_ids):
    """ scrape webpage """
    gene_evidence = []
    for gene_id in gene_ids:
        url = 'https://ckb.jax.org/gene/show?geneId={}'.format(gene_id['id'])
        page = requests.get(url, verify=False)
        tree = html.fromstring(page.content)

        # jax has a weid layout: a div with a table, with a thead, no tbody
        # and no rows
        xpath_thead_ths = '//*[@id="associatedEvidence"]/table/thead//th'
        xpath_tbody_tds = '//*[@id="associatedEvidence"]/table//td'

        # so, we grab the table heading
        thead_ths = tree.xpath(xpath_thead_ths)
        evidence_property_names = []
        for th in thead_ths:
            evidence_property_names.append(
                                    underscore(
                                        parameterize(
                                            unicode(th.text.strip()))))

        # grab all the TD's and load an array of evidence
        tds = tree.xpath(xpath_tbody_tds)
        if len(tds) == 0:
            logging.info('no table tds found. skipping')
            break
        td_texts = [td.text_content().strip() for td in tds]
        cell_limit = len(td_texts)
        evidence = []
        i = 0
        while True:
            e = {}
            for name in evidence_property_names:
                e[name] = td_texts[i]
                i = i + 1
            e['references'] = e['references'].split()
            if 'detail...' in e['references']:
                e['references'].remove('detail...')
            evidence.append(e)
            if (i >= cell_limit):
                break
        yield {'gene': gene_id['gene'], 'jax_id': gene_id['id'], 'evidence': evidence}  # NOQA


def convert(jax_evidence):
    gene = jax_evidence['gene']
    jax = jax_evidence['jax_id']
    evidence_array = jax_evidence['evidence']
    for evidence in evidence_array:

        # TODO: alterations are treated individually right now, but they are
        # actually combinations and should be treated accordingly.

        # Parse molecular profile and use for variant-level information.
        genes_from_profile, tuples = _parse(evidence['molecular_profile'])

        features = []
        for tuple in tuples:
            feature = {}
            feature['geneSymbol'] = tuple[0]
            feature['name'] = ' '.join(tuple[1:])
            feature['biomarker_type'] = mut.norm_biomarker(None)

            try:
                """
                 filter out
                 "FLT3 D835X FLT3 exon 14 ins"
                """
                exceptions = set(["exon", "ins", "amp", "del", "exp", "dec"])
                profile = set(tuple)
                if len(exceptions.intersection(profile)) > 0:
                    print 'skipping ', evidence['molecular_profile']
                    matches = []
                else:
                    # Look up variant and add position information.
                    if not LOOKUP_TABLE:
                        LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                                        "./cosmic_lookup_table.tsv")
                    matches = LOOKUP_TABLE.get_entries(tuple[0],
                                                       ' '.join(tuple[1:]))
                if len(matches) > 0:
                    # FIXME: just using the first match for now;
                    # it's not clear what to do if there are multiple matches.
                    match = matches[0]
                    feature['chromosome'] = str(match['chrom'])
                    feature['start'] = match['start']
                    feature['end'] = match['end']
                    feature['ref'] = match['ref']
                    feature['alt'] = match['alt']
                    feature['referenceName'] = str(match['build'])
            except:
                pass
            features.append(feature)

        association = {}
        association['description'] = evidence['efficacy_evidence']
        association['environmentalContexts'] = []
        association['environmentalContexts'].append({
            'description': evidence['therapy_name']})
        association['phenotype'] = {
            'description': evidence['indication_tumor_type']
        }
        association['evidence'] = [{
            "evidenceType": {
                "sourceName": "jax"
            },
            'description': evidence['response_type'],
            'info': {
                'publications': [
                    ['http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(r) for r in evidence['references']]  # NOQA
                ]
            }
        }]
        # add summary fields for Display
        association = el.evidence_label(evidence['approval_status'],
                                        association)
        association = ed.evidence_direction(evidence['response_type'],
                                            association)

        if len(evidence['references']) > 0:
            association['publication_url'] = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(evidence['references'][0])  # NOQA
        association['drug_labels'] = evidence['therapy_name']
        feature_association = {'genes': genes_from_profile,
                               'feature_names': evidence['molecular_profile'],
                               'features': features,
                               'association': association,
                               'source': 'jax',
                               'jax': evidence}
        yield feature_association


def harvest_and_convert(genes):
    """ get data from jax, convert it to ga4gh and return via yield """
    for jax_evidence in harvest(genes):
        # print "harvester_yield {}".format(jax_evidence.keys())
        for feature_association in convert(jax_evidence):
            # print "jax convert_yield {}".format(feature_association.keys())
            yield feature_association


def _parse(molecular_profile):
    """ returns gene, tuples[] """
    molecular_profile = molecular_profile.replace(' - ', '-')
    parts = molecular_profile.split()
    gene = None
    # gene_complete = True

    tuples = []
    tuple = None
    fusion_modifier = ''
    for idx, part in enumerate(parts):
        if not gene:
            gene = part
        # # deal with 'GENE - GENE '
        # if part == '-':
        #     gene += part
        #     gene_complete = False
        #     continue
        # elif not gene_complete:
        #     gene += part
        #     gene_complete = True
        #     continue

        if not tuple:
            tuple = []
        # build first tuple
        if len(tuples) == 0:
            if len(tuple) == 0 and '-' not in gene:
                tuple.append(gene)

        if idx == 0:
            continue

        # ignore standalone plus
        if not part == '+':
            tuple.append(part)

        # we know there is at least one more to fetch before terminating tuple
        if len(tuple) == 1 and idx < len(parts)-1:
            continue

        # is the current tuple complete?
        if (
                (len(tuple) > 1 and part.isupper()) or
                idx == len(parts)-1 or
                parts[idx+1].isupper()
           ):
                if len(tuple) == 1 and tuple[0].islower():
                    fusion_modifier = ' {}'.format(tuple[0])
                else:
                    tuples.append(tuple)
                tuple = None

    # if gene is a fusion, render genes separately
    if ('-' in gene):
        fusion = gene
        first_gene, second_gene = gene.split('-')
        tuples.append([first_gene, fusion + fusion_modifier])
        tuples.append([second_gene, fusion + fusion_modifier])
        gene = first_gene

    # if gene in tuples is fusion re-render
    def is_fusion(tuple):
        return '-' in tuple[0]

    non_fusion_tuples = [x for x in tuples if not is_fusion(x)]
    fusion_tuples = [x for x in tuples if is_fusion(x)]
    for tuple in fusion_tuples:
        fusion = tuple[0]
        first_gene, second_gene = fusion.split('-')
        non_fusion_tuples.append([first_gene, fusion])
        non_fusion_tuples.append([second_gene, fusion])
    tuples = non_fusion_tuples

    # get set of all genes
    genes = set([])
    for tuple in tuples:
        genes.add(tuple[0])

    return sorted(list(genes)), tuples


def _test():
    for feature_association in harvest_and_convert(None):
        print feature_association
        break

if __name__ == '__main__':
    _test()
