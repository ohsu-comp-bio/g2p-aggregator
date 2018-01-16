from __future__ import division

# data manipulation
from g2p_client import G2PDatabase
import pandas as pd
from elasticsearch_dsl import Search, Q

# plotting
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pylab import figure
# other
import argparse
import hashlib
import json
from collections import namedtuple


class Cohorts(object):
    def __init__(self, es_host, index='associations',
                 genie_variants='../data/data_mutations_extended_1.0.1.txt',
                 genie_clinical='../data/data_clinical_1.0.1.txt'):
        self.db = G2PDatabase(es_host, index)
        self.index = index
        self.associations_df = self.db.associations_dataframe()
        self.genie_associations_df = self.db.genie_associations(self.associations_df, genie_variants, genie_clinical)


    def g2p_phenotypes_by_source_figure(self, n=20, path=None):
        """ show the top N phenotypes """
        sns.set(font_scale=2)
        table = pd.pivot_table(self.associations_df,
                               index=["phenotype.term", "source"],
                               values=['evidence.id'],
                               aggfunc=lambda _id: len(_id.unique()),
                               fill_value=0)

        cmp = plt.cm.get_cmap('jet')
        s_sort = table.groupby(level=[0]).sum().sort_values(by=['evidence.id'],ascending=False)
        table = table.reindex(index=s_sort.index, level=0).unstack(fill_value=0)
        ax = table.head(20).plot(kind='bar',  stacked=True,  figsize=(24, 16))
        fig = ax.get_figure()
        if path:
            fig.savefig(path, bbox_inches='tight')
        return fig

    def g2p_phenotypes_by_chromosome_figure(self, path=None):
        """ show the phenotypes mapped to feature chromosome """
        # create a pivot table to sum evidence count by phenotype and chromosome
        table = pd.pivot_table(self.associations_df,
                               index=['feature.chromosome'],
                               columns=['phenotype.term'],
                               values=['evidence.id'],
                               aggfunc=lambda _id: len(_id.unique()),
                               fill_value=0)
        # map X to 23
        a = table.index.to_series().str.replace('X','23').astype(int).sort_values()
        table = table.reindex(index=a.index)
        ax = table.plot(kind='bar',  stacked=True,  figsize=(24, 16), legend=None)
        fig = ax.get_figure()
        if path:
            fig.savefig(path, bbox_inches='tight')
        return fig

    def genie_samples_by_chromosome_figure(self, path=None):
        # create a pivot table to sum barcode count by phenotype and chromosome
        table = pd.pivot_table(self.genie_associations_df,
                               index=['feature.chromosome'],
                               columns=['phenotype.term'],
                               values=['Tumor_Sample_Barcode'],
                               aggfunc=lambda _id: len(_id.unique()),
                               fill_value=0)
        # map X to 23
        a = table.index.to_series().str.replace('X','23').astype(int).sort_values()
        table = table.reindex(index=a.index)
        ax = table.plot(kind='bar',  stacked=True,  figsize=(24, 16), legend=None)
        fig = ax.get_figure()
        if path:
            fig.savefig(path, bbox_inches='tight')
        return fig

    def genie_samples_by_oncotree_figure(self, path=None):
        # create a pivot table to sum barcode count by source and ONCOTREE_CODE
        table = pd.pivot_table(self.genie_associations_df,
                               index=['ONCOTREE_CODE'],
                               columns=['source'],
                               values=['Tumor_Sample_Barcode'],
                               aggfunc=lambda _id: len(_id.unique()),
                               fill_value=0,
                               margins=True
                               )
        # sort by the All column total
        table.sort_values(by=('Tumor_Sample_Barcode', 'All'), ascending=False,inplace=True)
        # now that we are sorted drop the All row and column
        table.drop('All',inplace=True)
        table.drop('All', axis=1, level=1,inplace=True)
        # plot the top 20
        ax = table.head(20).plot(kind='bar',  stacked=True,  figsize=(24, 16) )
        fig = ax.get_figure()
        if path:
            fig.savefig(path, bbox_inches='tight')
        return fig

    def genie_biomarkers_figure(self, n=20, path=None):
        # create a pivot table to sum barcode count by biomarker_type and ONCOTREE_CODE

        simple_biomarker_types = ['snp', 'mutant', 'nonsense', 'splice', 'deletion', 'polymorphism', 'synonymous']
        table =  self.genie_associations_df.loc[self.genie_associations_df['feature.biomarker_type'].isin(simple_biomarker_types)]

        table =  pd.pivot_table(table,
            index=['feature.biomarker_type'],
            columns=['ONCOTREE_CODE' ],
            values=['Tumor_Sample_Barcode'],
            aggfunc=lambda _id: len(_id.unique()),
            fill_value=0,
            margins = True)


        def col_contents(x):
            """ sort column order based on contents of All row"""
            # x = ('Tumor_Sample_Barcode', 'AASTR')
            return table.loc['All':'All', (x[0], x[1])]['All']

        # sort by the All column total
        table.sort_values(by=('Tumor_Sample_Barcode', 'All'), ascending=False, inplace=True)
        table.sort_index(axis=1, level=0,inplace=True)
        table = table.reindex_axis(sorted(table.columns, key=col_contents, reverse=True), axis=1)


        # now that we are sorted drop the All row and column
        table.drop('All',inplace=True)
        table.drop('All', axis=1, level=1,inplace=True)
        # drop all except top twenty
        table.drop(table.columns[range(n,len(table.columns))],axis=1,inplace=True)

        # https://seaborn.pydata.org/generated/seaborn.heatmap.html
        sns.set(font_scale=1)
        # Draw a heatmap with the numeric values in each cell
        fig, ax = plt.subplots(figsize=(18, 12))
        # sns.heatmap(table, fmt="1.0f", linewidths=.5, ax=ax, cbar=False, cmap="YlGnBu",  )
        sns.heatmap(table, cmap="YlGnBu")
        if path:
            fig.savefig(path, bbox_inches='tight')
        return fig


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--index',
                           help='index to use',
                           default='associations',
                           )
    argparser.add_argument('--host',
                           help='elastic host',
                           default='localhost',
                           )
    argparser.add_argument("-v", "--verbose", help="increase output verbosity",
                           default=False,
                           action="store_true")
    args = argparser.parse_args()
    print 'producing g2p_phenotypes_by_source, may take several minutes.'
    cohorts = Cohorts(es_host=args.host, index=args.index)
    cohorts.g2p_phenotypes_by_source_figure(path='./images/g2p_phenotypes_by_source.png')
    print 'producing g2p_phenotypes_by_chromosome, may take several minutes.'
    cohorts.g2p_phenotypes_by_chromosome_figure(path='./images/g2p_phenotypes_by_chromosome.png')
    print 'producing genie_samples_by_chromosome, may take several minutes.'
    cohorts.genie_samples_by_chromosome_figure(path='./images/genie_samples_by_chromosome.png')
    print 'producing genie_samples_by_oncotree, may take several minutes.'
    cohorts.genie_samples_by_oncotree_figure(path='./images/genie_samples_by_oncotree.png')
    print 'producing genie_biomarkers, may take several minutes.'
    cohorts.genie_biomarkers_figure(path='./images/genie_biomarkers.png')
