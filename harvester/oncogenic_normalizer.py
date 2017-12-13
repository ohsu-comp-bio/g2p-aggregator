
import sys
import re
import pandas
from copy import deepcopy


def parse_genomic_locus(locus):
    locii_return_set = []
    locii = locus.split(',')
    for gl in locii:
        parts = gl.split(':')
        # insertions and deletions
        if 'del' in gl or 'ins' in gl:
            s = re.match('([0-9]*)[0-9_]*([A-Z]*)[a-z]*([A-Z]*)', parts[1].strip('g.'))
            locii_return_set.append([parts[0].strip('chr'), s.group(1), s.group(2), s.group(3)])
        # mutations
        elif '>' in gl:
            s = re.match('([0-9]*)([A-Z]*)>([A-Z]*)', parts[1].strip('g.'))
            locii_return_set.append([parts[0].strip('chr'), s.group(1), s.group(2), s.group(3)])
        # duplications (specific insertions)
        elif 'dup' in gl:
            s = re.match('([0-9]*)[0-9_]*([A-Z]*)[a-z]*([A-Z]*)', parts[1].strip('g.'))
            locii_return_set.append([parts[0].strip('chr'), s.group(1), s.group(3), ''])
        else: 
            raise SyntaxError('missed a case!')
    return locii_return_set

def normalize_cgi_oncogenic(asso, gene_set):
    # add the asso to the set before edits are made
    asso_set = [asso]
    new_asso = deepcopy(asso)
    # grab only oncogenic mutations from cgi table that match gene and tumor
    CGI_TABLE = None
    if not CGI_TABLE:
        CGI_TABLE = CGI_Oncogenic('../data/cgi_oncogenic_mutations.tsv')
    tt = new_asso['cgi']['Primary Tumor type']
    for gene in gene_set:
        for match in CGI_TABLE.get_muts(gene, tt):
            # replicate relevant feature set (in case there's more than one)
            for feature in new_asso['features']:
                if gene == feature['geneSymbol']:
                    # Look up position info
                    for locus in parse_genomic_locus(match['gdna']):
                        feature['name'] = gene + match['gdna']
                        feature['chromosome'] = locus[0]
                        feature['start'] = locus[1]
                        feature['ref'] = locus[2]
                        feature['alt'] = locus[3]
            new_asso['association']['cgiValidatedOncogenicMutations'] = match
            asso_set.append(new_asso)
    return asso_set


def normalize_oncokb_oncogenic(asso, gene_set):
    asso_set = [asso]
    new_asso = deepcopy(asso)
    # make some edits to new_asso
    ONCOKB_TABLE = None
    if not ONCOKB_TABLE:
        ONCOKB_TABLE = ONCOKB_Oncogenic('../data/oncokb_all_mutations.tsv')
    for gene in gene_set:
        for match in ONCOKB_TABLE.get_muts(gene):
            for feature in new_asso['features']:
                if gene == feature['geneSymbol']:
                    feature['name'] = match['Alteration']
                    # catch locus edits later; from COSMIC? CGI?
            new_asso['association']['oncokbOncogenicMutations'] = match
            asso_set.append(new_asso)
    return asso_set



def normalize_feature_association(feature_association):
    # we only care about oncogenic mutations here
    asso = feature_association[0]
    association = asso['association']
    source = asso['source']
    genes = asso['genes']
    if 'oncogenic' not in association:
        return feature_association
    if source == 'cgi':
        return normalize_cgi_oncogenic(asso, genes)
    elif source == 'oncokb':
        return normalize_oncokb_oncogenic(asso, genes)

class CGI_Oncogenic(object):
    """
    Parses downloaded TSV of validated oncogenic mutations from CGI and searches for oncogenic mutations by gene:
    https://www.cancergenomeinterpreter.org/mutations
    """
    def __init__(self, mut_file):
        self.muts = pandas.read_csv(mut_file, sep='\t')
        self.gene_df_cache = {}

    def get_muts(self, gene, tumor):
        if gene in self.gene_df_cache:
            muts = self.gene_df_cache[gene]
        else:
            muts = self.muts[self.muts['gene'] == gene]
            self.gene_df_cache[gene] = muts
        muts = muts[muts['cancer_acronym'].str.contains(tumor + '|CANCER')]
        return muts.to_dict(orient='records')

class ONCOKB_Oncogenic(object):
    """
    Parses downloaded TSV of all mutations from OncoKB and searches for oncogenic mutations by gene: 
    http://oncokb.org/#/dataAccess
    """
    def __init__(self, mut_file):
        self.muts = pandas.read_csv(mut_file, sep='\t')
        self.gene_df_cache = {}

    def get_muts(self, gene):
        if gene in self.gene_df_cache:
            muts = self.gene_df_cache[gene]
        else:
            muts = self.muts[self.muts['Gene'] == gene]
            self.gene_df_cache[gene] = muts
        muts = muts[muts['Oncogenicity'].str.contains('Oncogenic')].fillna('')
        return muts.to_dict(orient='records')




