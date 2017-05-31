import pandas
import json
import copy

import cosmic_lookup_table
import evidence_label as el

""" https://www.cancergenomeinterpreter.org/biomarkers """

LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup("./cosmic_lookup_table.tsv")


def _get_evidence(gene_ids, path='./cgi_biomarkers_20170208.tsv'):
    """ load tsv """
    df = pandas.read_table(path)
    # change nan to blank string
    df = df.fillna('')
    # if no gene list return all
    if not gene_ids:
        dict_list = df.to_dict(orient='records')
    else:
        rows = df.loc[df['Gene'].isin(gene_ids)]
        dict_list = rows.to_dict(orient='records')
    for row in dict_list:
        yield row


def convert(evidence):
    """
    ['Primary Tumor type', 'Drug family', 'Alteration type', 'Targeting',
    'Assay type', 'Evidence level', 'Biomarker', 'Drug', 'Alteration',
    'Source', 'Curator', 'Comments', 'Drug status', 'Drug full name',
    'TCGI included', 'Curation date', 'Gene', 'Metastatic Tumor Type',
    'Association']
    {'Primary Tumor type': 'GIST', 'Drug family': '[HSP90 inhibitor]',
     'Alteration type': 'MUT', 'Targeting': nan, 'Assay type': nan,
     'Evidence level': 'Pre-clinical',
     'Biomarker': 'KIT mutation in exon 9 or 17',
     'Drug': '[]',
     'Alteration': 'KIT:788-828,449-514',
     'Source': 'PMID:21737509', 'Curator': 'RDientsmann',
     'Comments': nan, 'Drug status': nan,
     'Drug full name': 'HSP90 inhibitors',
     'TCGI included': True, 'Curation date': '01/16',
     'Gene': 'KIT', 'Metastatic Tumor Type': nan,
     'Association': 'Responsive'}
    """
    gene = evidence['Gene']
    feature = {}
    feature['geneSymbol'] = gene
    feature['name'] = evidence['Biomarker']
    feature['description'] = evidence['Alteration']

    association = {}
    association['description'] = '{} {} {}'.format(gene,
                                                   evidence['Drug full name'],
                                                   evidence['Association'])
    association['environmentalContexts'] = []
    association['environmentalContexts'].append({
        'description': evidence['Drug full name']})
    phenotype_description = evidence['Primary Tumor type']
    if not evidence['Metastatic Tumor Type'] == '':
        phenotype_description = '{} {}'.format(
                phenotype_description, evidence['Metastatic Tumor Type'])
    association['phenotype'] = {
        'description': phenotype_description
    }

    pubs = []
    for p in evidence['Source'].split(';'):
        t = None
        if ':' in p:
            t, id = p.split(':')
        if t == 'PMID':
            pubs.append('http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(id))
        else:
            pubs.append('https://www.google.com/#q={}'.format(p))

    association['evidence'] = [{
        "evidenceType": {
            "sourceName": "cgi"
        },
        'description': evidence['Association'],
        'info': {
            'publications': pubs
        }
    }]
    # add summary fields for Display

    for item in el.ev_lab:
        for opt in el.ev_lab[item]:
            if opt in evidence['Evidence level'].lower():
                association['evidence_label'] = item
    if 'evidence_label' not in association:
        association['evidence_label'] = evidence['Evidence level']

    for item in el.res_type:
        for opt in el.res_type[item]:
            if opt in evidence['Association'].lower():
                association['response_type'] = item
    if 'response_type' not in association:
        association['response_type'] = evidence['Association']

    association['publication_url'] = pubs[0]
    association['drug_labels'] = evidence['Drug full name']
    feature_association = {'gene': gene,
                           'feature': feature,
                           'association': association,
                           'source': 'cgi',
                           'cgi': evidence}

    # For each biomarker, add more feature information and yield.
    fields = evidence['Alteration'].split(':')
    if len(fields) == 2:
        gene, hgvs_p = fields
        for protein_change in hgvs_p.split(','):
            matches = LOOKUP_TABLE.get_entries(gene, protein_change)
            if len(matches) > 0:

                # FIXME: just using the first match for now;
                # it's not clear what to do if there are multiple matches.
                match = matches[0]
                detailed_feature = copy.deepcopy(feature)
                detailed_feature['chromosome'] = match['chrom']
                detailed_feature['start'] = match['start']
                detailed_feature['end'] = match['end']
                detailed_feature['referenceName'] = match['build']
                # TODO: add alteration type.

                feature_association['feature'] = detailed_feature

            yield feature_association
    else:
        yield feature_association


def harvest(genes=None, drugs=None):
    """ get data from cgi """
    for evidence in _get_evidence(genes):
        yield evidence


def harvest_and_convert(genes=None, drugs=None):
    """ get data from cgi, convert it to ga4gh and return via yield """
    for evidence in harvest(genes, drugs):
        # print "harvester_yield {}".format(evidence.keys())
        # print evidence
        for feature_association in convert(evidence):
            # print "cgi convert_yield {}".format(feature_association.keys())
            yield feature_association


def _test():
    for feature_association in harvest_and_convert(['KIT']):
        print feature_association.keys()

if __name__ == '__main__':
    _test()
