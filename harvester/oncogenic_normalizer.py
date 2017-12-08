
import pandas


def normalize_cgi_oncogenic(asso, gene):
    # grab only oncogenic mutations from cgi table that match gene
    CGI_TABLE = None
    if not CGI_TABLE:
        CGI_TABLE = CGI_Oncogenic('../data/cgi_oncogenic_mutations.tsv')
    matches = CGI_TABLE.get_muts(gene)
    print 'SET MATCHES:', matches
    # keep muts which match cancer type
    tt = asso['cgi']['Primary Tumor type']
    for match in matches:
        cancer_set = match['cancer_acronym'].replace('-PR', '').split(';')
        if tt in cancer_set or 'CANCER' in cancer_set:
            print match
    return


def normalize_feature_association(feature_association):
    # we only care about oncogenic mutations here
    association = feature_association['association']
    source = feature_association['source']
    genes = feature_association['genes']
    if 'oncogenic' not in association:
        return
    if source == 'cgi':
        if len(genes) > 1:
            raise SyntaxError
        normalize_cgi_oncogenic(feature_association, genes[0])


class CGI_Oncogenic(object):
    """
    Parses downloaded TSV of validated oncogenic mutations from CGI and searches for ongenic mutations by gene:
https://www.cancergenomeinterpreter.org/mutations
    """
    def __init__(self, mut_file):
        self.muts = pandas.read_csv(mut_file, sep='\t')
        self.gene_df_cache = {}

    def get_muts(self, gene):
        if gene in self.gene_df_cache:
            muts = self.gene_df_cache['gene']
        else:
            muts = self.muts[self.muts['gene'] == gene]
            self.gene_df_cache[gene] = muts
        return muts.to_dict(orient='records')


