
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
        if 'del' in gl:
            s = re.match('([0-9]*)[0-9_]*([A-Z]*)[a-z]*([A-Z]*)', parts[1].strip('g.'))
            locii_return_set.append([parts[0].strip('chr'), s.group(1), s.group(3), s.group(2)])
        # mutations
        elif 'ins' in gl:
            s = re.match('([0-9]*)[0-9_]*([A-Z]*)[a-z]*([A-Z]*)', parts[1].strip('g.'))
            locii_return_set.append([parts[0].strip('chr'), s.group(1), s.group(2), s.group(3)])
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
    # grab only oncogenic mutations from cgi table that match gene and tumor
    CGI_TABLE = None
    features = deepcopy(asso['features'])
    if not CGI_TABLE:
        CGI_TABLE = CGI_Oncogenic('../data/cgi_oncogenic_mutations.tsv')
    tt = asso['cgi']['Primary Tumor type']
    # print "INSIDE FUNCTION", tt
    for gene in gene_set:
        print gene
        for match in CGI_TABLE.get_muts(gene, tt):
            print match
            # replicate relevant feature set (in case there's more than one)
            for feature in asso['features']:
                if gene == feature['geneSymbol']:
                    # print "GENE MATCH"
                    f = deepcopy(feature)
                    # Look up position info
                    for locus in parse_genomic_locus(match['gdna']):
                        f['name'] = gene + match['gdna']
                        f['chromosome'] = locus[0]
                        f['start'] = locus[1]
                        f['ref'] = locus[2]
                        f['alt'] = locus[3]
                        # f['cgiValidatedOncogenicMutations'] = match
                        features.append(f)
                        # print f
    asso['features'] = features
    return asso


def normalize_feature_association(feature_association):
    # we only care about oncogenic mutations here
    association = feature_association['association']
    source = feature_association['source']
    genes = feature_association['genes']
    if 'oncogenic' not in association:
        return
    if source == 'cgi':
        return normalize_cgi_oncogenic(feature_association, genes)
#    elif source == 'oncokb':
#        return normalize_oncokb_oncogenic(feature_association, genes)


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
        for idx, row in muts.iterrows():
            cts = row['cancer_acronym'].split(';')
            if tumor not in cts and 'CANCER' not in cts:
                muts.drop(idx, inplace=True)
        return muts.to_dict(orient='records')


# DEPRECATED
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
