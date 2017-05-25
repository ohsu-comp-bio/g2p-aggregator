
from lxml import html
from lxml import etree
import requests
from inflection import parameterize, underscore
import json

import cosmic_lookup_table

LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup("./cosmic_lookup_table.tsv")


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
        if len(thead_ths) == 0:
            print 'no table header found'
        evidence_property_names = []
        for th in thead_ths:
            evidence_property_names.append(
                                    underscore(
                                        parameterize(
                                            unicode(th.text.strip()))))

        # grab all the TD's and load an array of evidence
        tds = tree.xpath(xpath_tbody_tds)
        if len(tds) == 0:
            print 'no table tds found. skipping'
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
        molecular_profile_fields = evidence['molecular_profile'].split()
        for index in range(0, len(molecular_profile_fields), 2):
            feature = {}
            feature['geneSymbol'] = gene
            feature['name'] = evidence['molecular_profile']

            try:
                gene, alteration = molecular_profile_fields[index:index+2]
                # Look up variant and add position information.
                matches = LOOKUP_TABLE.get_entries(gene, alteration)
                if len(matches) > 0:
                    # FIXME: just using the first match for now;
                    # it's not clear what to do if there are multiple matches.
                    match = matches[0]
                    feature['chromosome'] = match['chrom']
                    feature['start'] = match['start']
                    feature['end'] = match['end']
                    feature['referenceName'] = match['build']
            except:
                pass

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
            association['evidence_label'] = evidence['response_type']
            if len(evidence['references']) > 0:
                association['publication_url'] = 'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(evidence['references'][0])  # NOQA
            association['drug_labels'] = evidence['therapy_name']
            feature_association = {'gene': gene,
                                   'feature': feature,
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
