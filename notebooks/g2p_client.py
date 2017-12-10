'''
Python client interface to G2P database.
'''

import sys
import argparse

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import OrderedDict
from itertools import product
import json
from pandas.io.json import json_normalize    
import copy


import pandas as pd


class G2PDatabase(object):
    '''
    The G2P database.
    '''

    def __init__(self, es_host, index='associations'):
        self.client = Elasticsearch(host=es_host)
        self.index = index

    def query_all(self, trials=False, size=1000, verbose=False):
        """
        Returns all documents in the database.
        
        :trials -- include trials, default False
        :size   -- number of rows to fetch in each chunk, default 1000
        :verbose -- print the query
        """
        s = Search(index=self.index).using(self.client).params(size=size)
        if trials:
            s = s.query("match_all")                
        else:
            s = s.query("query_string", query="-source:*trials")            
        s = s.source(excludes=['cgi', 'jax', 'civic', 'oncokb', 'molecularmatch_trials',
                              'molecularmatch', 'pmkb', 'sage', 'brca', 'jax_trials'])        
        if verbose:
            print s.to_dict()
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

    def feature_to_phenotypes(self, feature, verbose=False):
        '''
        Get phenotypes associated with a feature ( a dict )

        :feature -- a dict with ['source', 'evidence_label',
                                 'feature_chromosome', 'feature_start', 'feature_ref', 'feature_alt']
        :verbose -- print the query
        '''
        # map the df row to an elastic query
        query_string = ('+source:{} '
                        '+association.evidence_label:{} '
                        '+features.referenceName:GRCh37 '
                        '+features.chromosome:"{}" '
                        '+features.start:"{}" '
                        '+features.ref:"{}" '
                        '+features.alt:"{}"').format(
            feature['source'],
            feature['evidence_label'],
            feature['feature_chromosome'],
            feature['feature_start'],
            feature['feature_ref'],
            feature['feature_alt'])
        # create a search, ...
        s = Search(using=self.client, index=self.index)
        # with no data ..
        s = s.params(size=0)
        s = s.query("query_string", query=query_string)
        # ... just aggregations
        s.aggs.bucket('phenotype_descriptions','terms', field='association.phenotype.description.keyword') \
              .bucket('phenotype_id', 'terms', field='association.phenotype.type.id.keyword')
        if verbose:
            print s.to_dict()
        aggs = s.execute().aggregations
        # map it to an array of objects
        return [{'phenotype_description': b.key,
                 'phenotype_ontology_id': b.phenotype_id.buckets[0].key,
                 'phenotype_evidence_count':b.phenotype_id.buckets[0].doc_count} for b in aggs.phenotype_descriptions.buckets]

    
    def original_cgi_phenotypes(self, size=1000, verbose=False):
        '''
        Get original phenotype descriptions used by cgi
        :size -- number of documents to fetch per scan
        :verbose -- print the query
        '''
        # agg cgi phenotype_ids
        query_string = '+source:cgi '
        # create a search, ...
        s = Search(using=self.client, index=self.index)
        # with no data ..
        s = s.params(size=0)
        s = s.query("query_string", query=query_string)
        # ... just aggregations
        s.aggs.bucket('phenotype_ids', 'terms', field='association.phenotype.type.id.keyword')
        if verbose:
            print s.to_dict()
        aggs = s.execute().aggregations
        phenotype_ids = [b.key for b in aggs.phenotype_ids.buckets]
        if verbose:
            print phenotype_ids
        
        # get original cgi data
        query_string = '+source:cgi '
        s = Search(using=self.client, index=self.index)
        s = s.params(size=size)
        s = s.query("query_string", query=query_string) \
             .source(includes=['cgi', 'association.phenotype.type.id', 'association.phenotype.description'])    
        if verbose:
            print s.to_dict()
        # scan through entire set, deserialize original cgi payload and extract phenotype
        cgi_phenotypes = {}    
        for hit in s.scan():
            key = None
            if hit.association.phenotype.type.id:
                key = hit.association.phenotype.type.id 
            else:
                key = hit.association.phenotype.description 
            if key not in cgi_phenotypes:
                cgi_phenotypes[key] = set([])
                
            cgi = json.loads(hit.cgi)
            cgi_phenotypes[key].add(cgi['Primary Tumor acronym'])
        
        # xform set back to simple string        
        # consider items where it was the only tumor
        for key in cgi_phenotypes.keys():
            found = False
            originals = list(cgi_phenotypes[key])
            for original in originals:
                tumors = original.split(';')
                if len(tumors) == 1:
                    cgi_phenotypes[key] = tumors[0]
                    found = True
                    break
            if not found:
                cgi_phenotypes[key] = tumors[0]
        return cgi_phenotypes    
        

    def associations_dataframe(self, query_string=None, size=1000, verbose=False):
            '''
            Get a data frame with relevant information for analysis
            :query_string -- ES query string, defaults to only features with genomic location, no trials
            :size -- number of documents to fetch per scan
            :verbose -- print the query
            '''
            fields = ['source', 'association.evidence_label', 'genes', 'association.phenotype.type.id',
                      'association.phenotype.type.term', 'association.environmentalContexts.id',
                      'association.environmentalContexts.term', 'association.evidence.info.publications',
                      'features'
                     ]  
            if not query_string:
                query_string = ('-source:*trials '
                                '+features.start:* '
                                '+association.phenotype.type:* '
                                '+association.environmentalContexts.id:* '
                )
            s = Search(using=self.client, index=self.index)
            s = s.params(size=size)
            s = s.query("query_string", query=query_string).source(includes=fields)   
            if verbose:
                print s.to_dict()
            # creat df with the first level of json formatted by pandas            
            df = json_normalize([hit.to_dict() for hit in s.scan()])   

            # some generators to further denormalize creating a flat panda
            def environment_centric(df):
                """iterate through df. denormalize, create new row for each environment (drug) """
                for index, row  in df.iterrows():
                    for environmentalContext in row['association.environmentalContexts']:
                        ec = copy.deepcopy(environmentalContext)
                        ec.update(row)            
                        yield ec            

            def feature_centric(df):
                """iterate through df. denormalize, create new row for each feature (variant) """
                for index, row  in df.iterrows():
                    for feature in row['features']:
                        f = copy.deepcopy(feature)
                        f['gene_list'] = ','.join(row.genes)
                        f.update(row)            
                        yield f 

            def evidence_centric(df):
                """iterate through df. denormalize, create new row for each feature (variant) """
                for index, row  in df.iterrows():
                    for evidence in row['association.evidence']:
                        e = {}
                        e['publication_count'] = len(evidence['info']['publications'])
                        e.update(row)            
                        yield e

            df = pd.DataFrame(environment_centric(df))
            del df['association.environmentalContexts']
            df = pd.DataFrame(feature_centric(df))
            del df['features']
            del df['genes']
            df = pd.DataFrame(evidence_centric(df))
            del df['association.evidence']            
            return df
        
        
    
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
