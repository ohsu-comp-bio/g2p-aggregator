'''
Python client interface to G2P database.
'''

import sys
import argparse

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import OrderedDict
from itertools import product

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
        end_columns = ['description', 'evidence_label', 'evidence_direction', 'evidence_url']
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
            association_dict = hit['association'].to_dict()
            genes = hit['genes']
            if isinstance(genes, basestring):
                genes = [genes]
            hit_dict = {
                'source': hit['source'],
                'genes': ':'.join(genes),
                'drug': association_dict.get('drug_labels', ''),
                'description': hit['association']['description'],
                'evidence_label': association_dict.get('evidence_label', ''),
                'evidence_direction': association_dict.get('response_type', ''),
                'evidence_url': association_dict.get('publication_url', '')
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

    def summarize_results(self, s):
        '''
        Summarize results for a search by evidence level. Return value is a dict
        with the following keys: total_[A/B/C/D/E] and [source]_[A/B/C/D/E]
        '''

        # Create base dictionary with all needed keys.
        keys = ['%s_%s' % (source, evidence_label) \
                for (source, evidence_label) in product(['total'] + self.sources, ['A', 'B', 'C', 'D'])]
        rval = dict.fromkeys(keys, 0)

        if s.count() == 0:
            return rval

        hits_df = self.hits_to_dataframe(s)

        # Total counts for each evidence label.
        for evidence_label, count in hits_df.groupby('evidence_label').size().iteritems():
            rval['total_%s' % evidence_label] = count

        # Counts for each evidence label by source.
        size_series = hits_df.groupby(['source', 'evidence_label']).size()
        for (source, evidence_label), count in size_series.iteritems():
            rval['%s_%s' % (source, evidence_label)] = count
        return rval

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--host', help='ES host')
    parser.add_argument('-g', '--gene', help="Gene to query for")
    args = parser.parse_args()

    database = G2PDatabase(args.host)
    if args.gene:
        s = database.query_by_gene(args.gene)
    else:
        s = database.query_all()

    print database.hits_to_dataframe(s).to_csv(sep='\t', index=False, encoding='utf-8')
