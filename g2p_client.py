'''
Python client interface to G2P database.
'''

import sys

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from collections import OrderedDict

import pandas as pd


class G2PDatabase():

    def __init__(self, es_host, index='associations'):
        self.client = Elasticsearch(host=es_host)
        self.index = index

    def query_all(self):
        '''
        Returns all documents in the database.
        '''
        s = Search(index=self.index).using(self.client).query("match_all")
        return s

    def query_by_gene(self, gene):
        '''
        Returns all matches for a gene.
        '''
        s = Search(index=self.index).using(self.client).query("match", gene=gene)
        s.execute()
        return s

    def query_gene_variants(self, gene):
        '''
        Returns all matches for a gene where the feature is a variant.
        '''
        pass

    def _hits_to_dataframe(self, s):
        start_columns = ['source', 'gene', 'drug']
        end_columns = ['description']
        feature_cols = ['feature_geneSymbol', 'feature_name', 'feature_entrez_id',
                        'feature_chromosome', 'feature_start', 'feature_end',
                        'feature_ref', 'feature_alt', 'feature_referenceName',
                        'feature_biomarker_type', 'feature_description', ]
        feature_dict_base = {}
        for col in feature_cols:
            feature_dict_base[col] = ''

        def _prepend_str_to_key(a_dict, prepend=''):
            for key in a_dict.keys():
                a_dict[prepend + key] = a_dict.pop(key)
            return a_dict

        data = []
        for _, hit in enumerate(s.scan()):
            hit_dict = {
                'source': hit['source'],
                'gene': hit['gene'],
                'drug': hit['association'].to_dict().get('drug_labels', ''),
                'description': hit['association']['description']
            }
            feature_dict = feature_dict_base.copy()
            feature_dict.update(_prepend_str_to_key(hit['feature'].to_dict(), 'feature_'))
            hit_dict.update(feature_dict)
            data.append(hit_dict)

        df = pd.DataFrame(data)
        if len(df) > 0:
            df = df[start_columns + feature_cols + end_columns]
        return df


if __name__ == '__main__':
    database = G2PDatabase(sys.argv[1])
    s = database.query_all()
    print database._hits_to_dataframe(s).to_csv(sep='\t', index=False, encoding='utf-8')
