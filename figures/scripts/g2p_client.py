'''
Python client interface to G2P database.
'''

import sys
import argparse
import ast


from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import OrderedDict
from itertools import product
import json
from pandas.io.json import json_normalize
import copy

import location_normalizer


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
        start_columns = ['source', 'genes', 'drug', 'phenotype', 'cgi_phenotype']
        end_columns = ['description', 'evidence_label', 'evidence_direction', 'evidence_url', 'oncogenic']
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
            if 'cgi' in hit:
                cgi_dict = ast.literal_eval(hit['cgi'])
            else:
                cgi_dict = {}
            genes = hit['genes']
            if isinstance(genes, basestring):
                genes = [genes]
            hit_dict = {
                'source': hit['source'],
                'genes': ':'.join(genes),
                'drug': association_dict.get('drug_labels', ''),
                'phenotype': association_dict.get('phenotype', {'type': {'term': ''}})
                                             .get('type', {'term': ''})
                                             .get('term', ''),
                'cgi_phenotype': cgi_dict.get('Primary Tumor acronym', ''),
                'description': hit['association']['description'],
                'evidence_label': association_dict.get('evidence_label', ''),
                'evidence_direction': association_dict.get('response_type', ''),
                'evidence_url': association_dict.get('publication_url', ''),
                'oncogenic': association_dict.get('oncogenic', '')
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


    def associations_dataframe(self, query_string=None, size=1000, verbose=False):
            '''
            Get a data frame with relevant information for analysis.
            By default this excludes trials and limited to evidence with fully normalized features, environment and phenotype
            :query_string -- ES query string, defaults to only features with genomic location, no trials
            :size -- number of documents to fetch per scan
            :verbose -- print the query
            '''
            fields = ['source', 'association.evidence_label', 'association.response_type', 'genes', 
                      'association.phenotype.type.id',
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
                print json.dumps(s.to_dict(),indent=2, separators=(',', ': '))

            def hit_with_id(hit):
                '''include the unique id with the source data'''
                h = hit.to_dict()
                h['evidence.id'] = hit.meta.id
                return h

            # create df with the first level of json formatted by pandas
            df = json_normalize([hit_with_id(hit) for hit in s.scan()])

            # some generators to further denormalize creating a flat panda
            def environment_centric(df):
                """iterate through df. denormalize, create new row for each environment (drug) """
                for index, row  in df.iterrows():
                    for environmentalContext in row['association.environmentalContexts']:
                        ec = copy.deepcopy(environmentalContext)
                        for n in ['id', 'term']:
                            if n in ec:
                                ec['environmentalContext.{}'.format(n)] = ec.pop(n)
                        ec.update(row)
                        yield ec

            def feature_centric(df):
                """iterate through df. denormalize, create new row for each feature (variant) """
                for index, row  in df.iterrows():
                    for feature in row['features']:
                        f = copy.deepcopy(feature)
                        genomic_hgvs = location_normalizer.genomic_hgvs(f)
                        # skip any embedded features w/out coordinates
                        if genomic_hgvs is None:
                            genomic_hgvs = 'no_hgvs:{}'.format(f['name'].encode('ascii', 'ignore'))
                            continue
                        f['genomic_hgvs'] = genomic_hgvs
                        f['gene_list'] = ','.join(row.genes)
                        # decorate the feature components with 'feature.' prefix
                        for n in ['start', 'ref','alt', 'description', 'entrez_id', 'geneSymbol',
                                   'chromosome', 'name', 'referenceName', 'end','biomarker_type', 'genomic_hgvs']:
                            if n in f:
                                f['feature.{}'.format(n)] = f.pop(n)
                        if 'links' in f:
                            del f['links']
                        if 'synonyms' in f:
                            del f['synonyms']
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

            rename = {'association.evidence_label': 'evidence_label',
             'association.response_type': 'response_type',
             'association.phenotype.type.id': 'phenotype.id',
             'association.phenotype.type.term': 'phenotype.term'}
            df = df.rename(columns=rename)
            denormalization_msg = {}
            denormalization_msg['original'] = len(df)
            df = pd.DataFrame(environment_centric(df))
            denormalization_msg['environment_centric'] = len(df)
            del df['association.environmentalContexts']
            df = pd.DataFrame(feature_centric(df))
            denormalization_msg['feature_centric'] = len(df)
            del df['features']
            del df['genes']
            df = pd.DataFrame(evidence_centric(df))
            denormalization_msg['evidence_centric'] = len(df)
            if verbose:
                print json.dumps(denormalization_msg,indent=2, separators=(',', ': '))

            del df['association.evidence']
            return df


    def genie_associations(self, associations_df, genie_variants_path, genie_clinical_path):
            '''
            join the genie data with the association dataframe
            :associations_df -- existing associations_df
            :genie_variants_path -- full path name to genie variants
            :genie_clinical_path -- full path name to genie clinical
            '''
            # Load GENIE variants.
            # prevents `DtypeWarning`
            # map unknown (all null) types,
            # see https://wiki.nci.nih.gov/display/TCGA/Mutation+Annotation+Format+(MAF)+Specification
            # (17,18,23,24,25,29)
            dtype={"Match_Norm_Seq_Allele1": str,
                   "Match_Norm_Seq_Allele2": str,
                   "Verification_Status": str,
                   "Validation_Status": str,
                   "Mutation_Status": str,
                   "Score": str
                  }
            genie_variants_df = pd.read_csv(genie_variants_path, sep='\t', comment='#', dtype=dtype)
            genie_clinical_df = pd.read_csv(genie_clinical_path, sep='\t', comment='#')

            # join clinical and variants
            genie_clinical_df.set_index(['SAMPLE_ID'])
            genie_variants_df.set_index(['Tumor_Sample_Barcode'])

            genie_df = pd.concat([genie_variants_df, genie_clinical_df], axis=1)
            genie_df.groupby(['Tumor_Sample_Barcode'])

            # resulting data set should have same length as variants
            if not len(genie_df) == len(genie_variants_df):
                # verify sample keys joining variants and clinical
                sys.stderr.write('ERROR: clinical_df joined with genie_variants_df unexpected length')
                sys.stderr.write('clinical_df samples len %s' % len(genie_clinical_df['SAMPLE_ID']))
                sys.stderr.write('genie_df samples len %s' %  len(genie_variants_df['Tumor_Sample_Barcode']))
                sys.stderr.write('genie_clinical_df samples not in genie_df %s' %
                                 len(set(genie_clinical_df['SAMPLE_ID']) - set(genie_variants_df['Tumor_Sample_Barcode'])))
                sys.stderr.write('genie_df samples not in genie_clinical_df %s' %
                                 len(set(genie_variants_df['Tumor_Sample_Barcode']) -  set(genie_clinical_df['SAMPLE_ID'])))
                sys.stderr.write('genie_df  len %s' % len(genie_df))
                raise Exception('ERROR: genie_clinical_path joined with genie_variants_path unexpected length')
            # join combined variants/clinical with G2P
            genie_df.set_index(['Chromosome',
                           'Start_Position',
                           'End_Position',
                           'Reference_Allele',
                           'Tumor_Seq_Allele2'])

            associations_df.set_index(['feature.chromosome',
                                       'feature.start',
                                       'feature.end',
                                       'feature.ref',
                                       'feature.alt' ])
            # join the dataframes
            genie_associations_df = pd.concat([genie_df, associations_df], axis=1)
            genie_associations_df.groupby(['feature.chromosome', 'feature.start' , 'feature.end' ,
                                'feature.ref'    , 'feature.alt' ])

            if not len(genie_df) == len(genie_associations_df):
                sys.stderr.write('ERROR: genie_df  len %s' % len(genie_df))
                sys.stderr.write('associations_df  len %s' %  len(associations_df))
                sys.stderr.write('genie_associations_df  len %s' %  len(genie_associations_df))
                raise Exception('ERROR: genie_df joined with associations_df unexpected length')
            return genie_associations_df

    def harmonization_counts(self):
        def _aggregate_by_source(aggregation_name, query_string):
            """ simple terms count by source """
            # build query
            s = Search(using=self.client, index=self.index)
            s = s.params(size=0)
            s = s.query("query_string", query=query_string)
            s.aggs.bucket(aggregation_name, 'terms', field='source.keyword')
            # execute it
            agg = s.execute().aggregations
            # marshall to simple dict
            aggregation_name = dir(agg)[0]
            results = getattr(agg, aggregation_name)
            buckets = []
            for bucket in results.buckets:
                row = {'aggregation_name': aggregation_name}
                row['source'] = bucket.key
                row['value'] = bucket.doc_count
                buckets.append(row)
            return buckets
        # hold results
        aggs = []
        # name and query
        aggs.extend(_aggregate_by_source('harmonized_features', '+features.start:*'))
        aggs.extend(_aggregate_by_source('unharmonized_features', '-features.start:*'))
        aggs.extend(_aggregate_by_source('harmonized_biomarkers', '+features.biomarker_type:*'))
        aggs.extend(_aggregate_by_source('unharmonized_biomarkers', '-features.biomarker_type:*'))
        aggs.extend(_aggregate_by_source('harmonized_phenotype', '+association.phenotype.type.id:*'))
        aggs.extend(_aggregate_by_source('unharmonized_phenotype', '-association.phenotype.type.id:* '))
        aggs.extend(_aggregate_by_source('harmonized_environment', '+association.environmentalContexts.id:*'))
        aggs.extend(_aggregate_by_source('unharmonized_environment', '-association.environmentalContexts.id:*'))
        # make df
        df = pd.DataFrame([agg for agg in aggs])
        df.fillna(0, inplace=True)
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
