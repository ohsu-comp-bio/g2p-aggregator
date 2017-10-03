
import sys
from lxml import html
from lxml import etree
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from inflection import parameterize, underscore
import json
import re

import logging
import evidence_label as el
import evidence_direction as ed
import mutation_type as mut

import cosmic_lookup_table

LOOKUP_TABLE = None

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# see https://ckb.jax.org/about/curationMethodology


def _parse_profile(profile):
    parts = profile.split()
    global LOOKUP_TABLE
    if not LOOKUP_TABLE:
        LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                "./cosmic_lookup_table.tsv")
    parts = profile.split()
    # this list taken from https://ckb.jax.org/about/glossaryOfTerms
    # "Non specific variants" list, separated by space, where applicable
    jax_biomarker_types = [
        'act',
        'amp',
        'dec',
        'del',
        'exp',
        'fusion',
        'inact',
        'loss',
        'mut',
        'mutant',
        'negative',
        'over',
        'pos',
        'positive',
        'rearrange',
        'wild-type'
    ]
    gene_list = LOOKUP_TABLE.get_genes()
    genes = []
    muts = []
    biomarkers = []
    biomarker_types = None
    fusions = []
    # Complex loop: Run through the split profile, creating four arrays,
    # one of the indices of genes in `parts`, one of the indices of mutations
    # in `parts` (if present, `None` if not), one of biomarker strings, 
    # (if present, `None` if not), and a fusions array. Gene, mutation, and
    # biomarker arrays should always have same length. 
    for i in range(len(parts)):
        # check for fusions
        if '-' in parts[i] and parts[i] not in jax_biomarker_types:
            fusion = parts[i].split('-')
            if fusion[0] in gene_list and fusion[1] in gene_list:
                fusions.append(parts[i].split('-'))
                # if you're dealing with a fusion with no other gene listed, 
                # use the fusion as the gene
                if len(parts) > 1 and parts[i+1] not in gene_list:
                    genes.append(parts[i])
                    biomarker_types = []
                continue 
       # check to see if you're on a gene
        if parts[i] in gene_list:
            genes.append(parts[i])
            # reset the biomarker_type array on every new gene
            biomarker_types = []
            continue
        # check to see if part matches a mutation variant format, e.g. `V600E`
        if re.match("[A-Z][0-9]+[fs]?[*]?[0-9]?[A-Z]?", parts[i]):
            muts.append(parts[i])
            if i+1 == len(parts) or parts[i+1] in gene_list:
                biomarkers.append([''])
            continue
        # Should only hit this if there's no mutation listed for the present gene, 
        # so denote that and catch the biomarker.
        elif len(genes) != len(muts):
            muts.append('')
        if parts[i] in jax_biomarker_types:
            biomarker_types.append(parts[i])
            if i+1 == len(parts) or parts[i+1] in gene_list:
                biomarkers.append(biomarker_types)
        elif len(genes) != len(biomarkers):
            biomarkers.append([''])
    # change the internal biomarker_type arrays into strings
    biomarker_types = []
    for biomarker in biomarkers:
        if biomarker[0]:
            biomarker_types.append(' '.join(biomarker))
        else:
            biomarker_types.append('')
    return genes, muts, biomarker_types, fusions


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
    global LOOKUP_TABLE
    gene = jax_evidence['gene']
    jax = jax_evidence['jax_id']
    evidence_array = jax_evidence['evidence']
    for evidence in evidence_array:
        # TODO: alterations are treated individually right now, but they are
        # actually combinations and should be treated accordingly.

        # Parse molecular profile and use for variant-level information.
        profile = evidence['molecular_profile'].replace('Tp53', 'TP53').replace(' - ', '-')
        gene_index, mut_index, biomarkers, fusions  = _parse_profile(profile)

        if not (len(gene_index) == len(mut_index) == len(biomarkers)):
            print  "ERROR: This molecular profile has been parsed incorrectly!"
            print json.dumps({"molecular_profile": evidence['molecular_profile']}, indent=4, sort_keys=True)

        features = []
        parts = profile.split()
        for i in range(len(gene_index)):
            feature = {}
            feature['geneSymbol'] = gene_index[i]
            feature['name'] = ' '.join([gene_index[i], mut_index[i], biomarkers[i]])
            if biomarkers[i]:
                feature['biomarker_type'] = mut.norm_biomarker(biomarkers[i])
            else:
                feature['biomarker_type'] = mut.norm_biomarker('na')

            # Look up variant and add position information.
            if not LOOKUP_TABLE:
                LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                               "./cosmic_lookup_table.tsv")
            matches = LOOKUP_TABLE.get_entries(gene_index[i], mut_index[i])
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
            features.append(feature)
        for fusion in fusions:
            for gene in fusion:
                feature = {}
                feature['geneSymbol'] = gene
                feature['name'] = '-'.join(fusion)
                feature['biomarker_type'] = mut.norm_biomarker("fusion")
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
                'publications':
                    ['http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(r) for r in evidence['references']]  # NOQA
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
        feature_association = {'genes': ','.join(set(gene_index)),
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


def _test():
    for feature_association in harvest_and_convert(None):
        print feature_association
        break

if __name__ == '__main__':
    _test()
