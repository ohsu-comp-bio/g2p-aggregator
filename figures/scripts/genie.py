'''
Generate plots for GENIE analysis data.
'''

from __future__ import division

import pandas as pd
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from g2p_client import G2PDatabase

# Constants
HOST = 'dms-dev.compbio.ohsu.edu'
GENIE_VARIANTS = './data/data_mutations_extended_1.0.1.txt'
GENIE_CLINICAL = './data/data_clinical_1.0.1.txt'
evidence_levels = ['A', 'B', 'C', 'D']
evidence_directions = ['resistant', 'responsive']

class GENIEAnalysis:

    def __init__(self, variants_file=GENIE_VARIANTS,
                 clinical_file=GENIE_CLINICAL, g2p_df=None, occurence_thres=2):
        self.variants_file = variants_file
        self.clinical_file = clinical_file
        self.genie_df = None
        self.g2p_df = g2p_df
        self.occurence_thres = occurence_thres
        self.num_variants = 0
        self.num_donors = 0
        self.num_shared_variants = 0
        self.num_donors_with_shared_variants = 0

    def load(self):
        '''
        Load GENIE variants and clinical data and return complete dataframe.
        '''

        # Load GENIE variants.
        genie_variants = pd.read_csv(self.variants_file, sep='\t', comment='#')

        # Load GENIE clinical data.
        genie_clinical = pd.read_csv(self.clinical_file, sep='\t', comment='#')

        # Merge clinical data with variants.
        self.genie_df = pd.merge(genie_variants, genie_clinical, left_on=['Tumor_Sample_Barcode'], right_on=['SAMPLE_ID'])

        # Add count column to store total occurences of a variant.
        variant_counts = self.genie_df.groupby(['Chromosome', 'Start_Position', 'End_Position', 'Reference_Allele', 'Tumor_Seq_Allele2']).size().rename('count').reset_index()
        self.genie_df = pd.merge(self.genie_df, variant_counts, on=['Chromosome', 'Start_Position', 'End_Position', 'Reference_Allele', 'Tumor_Seq_Allele2'])

        # Set attributes.
        self.num_variants = len(self.genie_df)
        self.num_donors = get_num_donors(self.genie_df)
        shared_variants = self.get_shared_variants()
        self.num_shared_variants = len(shared_variants)
        self.num_donors_with_shared_variants = get_num_donors(shared_variants)

        return self.genie_df

    def get_shared_variants(self):
        return self.genie_df[self.genie_df['count'] >= self.occurence_thres]

    def donor_variant_histogram(self, filename='donor_variant_histogram'):
        '''
        Create histogram of variants per donor.
        '''
        x = self.genie_df['Tumor_Sample_Barcode'].value_counts().values
        data = [go.Histogram(x=x)]
        create_plot(data, title='GENIE: Variants per donor histogram',
                    xaxis_title='# variants per donor',
                    yaxis_title='count', filename=filename)

    def gene_variant_bar_chart(self, filename='gene_variant_counts'):
        '''
        Create plot of variants per gene.
        '''
        x = self.genie_df['Hugo_Symbol'].value_counts()
        data = [go.Bar(x=x.index, y=x.values)]
        create_plot(data, title='GENIE: Variants per donor histogram',
                    xaxis_title='# variants per donor',
                    yaxis_title='count', filename=filename)


# Helper methods.

def create_plot(data, layout=None, title='', xaxis_title= '', yaxis_title= '',
                width=600, height=600, filename='plot'):
    '''
    Create Plotly plot using offline approach.
    '''
    if not layout:
        layout = go.Layout(
            title=title,
            xaxis={
                'title': xaxis_title
            },
            yaxis={
                'title': yaxis_title
            },
            width=600,
            height=600
        )
    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename=filename)


def load_g2g2p_df():
    db = G2PDatabase(HOST)
    return db.associations_dataframe()

def get_num_donors(df):
    ''' Returns number of donors in a dataframe. '''
    return len(df['Tumor_Sample_Barcode'].unique())

def print_cohort_stats(df):
    '''
    Prints number of (a) variants; (b) unique variants; and (c) donors
    in a dataframe.
    '''
    print '-------------'
    print 'Number of variants: %i' % len(df)
    #print 'Number of unique variants: %i' % len(df[df['count'] > 1])
    print 'Number of donors: %i' % get_num_donors(df)
    print '-------------'

if __name__ == '__main__':
    genie_analysis = GENIEAnalysis()
    genie_analysis.load()

    print "All of GENIE"
    print_cohort_stats(genie_analysis.genie_df)

    print ''
    print "GENIE filtered for variant count >= %i" % genie_analysis.occurence_thres
    print_cohort_stats(genie_analysis.get_shared_variants())


    genie_analysis.donor_variant_histogram()
    genie_analysis.gene_variant_bar_chart()
