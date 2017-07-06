"""
Add drug_evidence_count, drug_evidence_url that denote knowledgebase results for each
entry in a table and output new table.
"""

import argparse

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import pandas as pd

from g2p_client import G2PDatabase

host = "dms-dev.compbio.ohsu.edu"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file", type=str, help="tabular input file")
    parser.add_argument("-sv", "--struct-vars", help="annotate structural variants", action="store_true")
    parser.add_argument("-l", "--label", help="label added to output", default=None)
    parser.add_argument("-f", "--filtered", help="Print only variants with results", action="store_true")
    args = parser.parse_args()
    label = args.label
    filtered = args.filtered

    # Read table.
    variants = pd.read_csv(args.in_file, sep=",")
    variants = variants.fillna('')

    # Annotate variants.
    database = G2PDatabase(host)

    # Add some flexibility when searching for gene name.
    gene_col_names = ['gene', 'Gene', 'Hugo_Symbol']
    gene_col_name = ''
    for name in gene_col_names:
        if name in variants.columns.values.tolist():
            gene_col_name = name
            break

    # Annotate variants by adding # of pieces of evidence + URL for each variant.
    variants['drug_evidence_count'] = 0
    variants['drug_evidence_url'] = ''
    for index, row in variants.iterrows():
        s = database.query_by_gene(row[gene_col_name])
        count = s.count()
        if count > 0:
            variants.iloc[index, -2:] = (count, 'https://dms-dev.compbio.ohsu.edu/g2p#gene%3A' + row[gene_col_name])

    if filtered:
        variants = variants[variants['drug_evidence_count'] > 0]
    print variants.to_csv(sep='\t', index=False, encoding='utf-8')



    # Annotate variants by joining each variant repeatedly with each piece of evidence.
    #
    # results_dfs = []
    # for index, row in variants.iterrows():
    #     s = database.query_by_gene(row['gene'])
    #     results_df = database._hits_to_dataframe(s)
    #     if len(results_df) > 0:
    #         merged_df = row.to_frame().transpose().merge(results_df, on="gene")
    #         if label:
    #             merged_df.insert(0, 'label', args.label)
    #         results_dfs.append(merged_df)
    #
    # print pd.concat(results_dfs).to_csv(sep='\t', index=False, encoding='utf-8')
