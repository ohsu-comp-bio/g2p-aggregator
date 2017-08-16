'''
Python client interface to G2P database.
'''

import sys
import argparse

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import OrderedDict

import pandas as pd


class G2PDatabase(object):
    '''
    The G2P database.
    '''

    def __init__(self, es_host, index='associations'):
        self.client = Elasticsearch(host=es_host)
        self.index = index

    def query_all(self):
        '''
        Returns all documents in the database.
        '''
        s = Search(index=self.index).using(self.client).query("match_all")
        return s

    def query_by_variant(self, chromosome, start, end, ref, alt):
        '''
        Returns all matches for a variant.
        '''
        q = Q('match', **{'features.chromosome': str(chromosome)}) & \
            Q('match', **{'features.start': start}) & \
            Q('match', **{'features.end': end}) & \
            Q('match', **{'features.ref': ref}) & \
            Q('match', **{'features.alt': alt})
        s = Search(index=self.index).using(self.client).query(q)
        s.execute()
        return s

    def query_by_gene(self, gene):
        '''
        Returns all matches for a gene.
        '''
        s = Search(index=self.index).using(self.client).query("match", genes=gene)
        s.execute()
        return s

    def query_gene_variants(self, gene):
        '''
        Returns all matches for a gene where the feature is a variant.
        '''
        pass

    def hits_to_dataframe(self, s):
        start_columns = ['source', 'genes', 'drug']
        end_columns = ['description', 'evidence_label', 'evidence_url']
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
                'genes': ':'.join(hit['genes']),
                'drug': hit['association'].to_dict().get('drug_labels', ''),
                'description': hit['association']['description'],
                'evidence_label': hit['association']['evidence_label'],
                'evidence_url': hit['association']['publication_url'],
            }

            # FIXME: this yields only the last feature of association, not all features.
            for i, feature in enumerate(hit['features']):
                feature_dict = feature_dict_base.copy()
                feature_dict.update(_prepend_str_to_key(feature.to_dict(), 'feature_'))
                hit_dict.update(feature_dict)
            data.append(hit_dict)

        df = pd.DataFrame(data)
        if len(df) > 0:
            df = df[start_columns + feature_cols + end_columns]
        return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--host", help="ES host")
    args = parser.parse_args()


    database = G2PDatabase(args.host)
    s = database.query_all()
    print database.hits_to_dataframe(s).to_csv(sep='\t', index=False, encoding='utf-8')
