'''
CGI Application
'''

from __future__ import division

import sys

import pandas as pd
pd.set_option('display.max_columns', 500)
import numpy as np
import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from g2p_client import G2PDatabase
from genie import *

# Constants
HOST = 'dms-dev.compbio.ohsu.edu'
GENIE_VARIANTS = '../../data/data_mutations_extended.txt'
GENIE_CLINICAL = '../../data/data_clinical.txt'
evidence_levels = ['A', 'B', 'C', 'D']


if __name__ == '__main__':
    site = G2PDatabase(HOST)
    g2p = site.associations_dataframe()
    g2p = g2p.fillna('')

    genie_instance = GENIEAnalysis()
    genie = genie_instance.load()

    g2p_grouped = g2p.groupby(['evidence_label',
                               'response_type',
                               'feature.alt',
                               'feature.biomarker_type',
                               'feature.chromosome',
                               'feature.genomic_hgvs',
                               'feature.name',
                               'feature.ref',
                               'feature.referenceName',
                               'feature.start',
                               'gene_list',
                               'phenotype.id',
                               'phenotype.term',
                               'source']).size().rename('count').reset_index()

    cgi_cancers = ['RA', 'SCHW', 'BLCA', 'PAAD', 'GBM', 'MA', 'COREAD', 'OV', 'RCCC', 'CM', 'LIP', \
                   'G', 'UCEC', 'SOLID', 'BRCA', 'AML', 'LUAD', 'SCC', 'BCC', 'GIST', 'HNSC', 'HCL', \
                   'CER', 'FRS', 'MESO', 'LUSC', 'BT', 'THCA', 'CH', 'L', 'NSCLC', 'LK', 'DLBCL', 'THYM', \
                   'ESCA', 'HNC', 'STAD', 'PA', 'ALL', 'SK', 'RPC', 'MEN', 'R',  'UVM', 'CTCL', 'PRAD', \
                   'AS', 'LY', 'HSEC', 'SCLC', 'ES', 'MERC', 'MM', 'HC', 'MPN', 'THF', 'S', 'NHLY', 'HLY', \
                   'CML', 'T', 'B', 'RHBDS', 'MDS', 'CLL', 'DFS', 'WT', 'M', 'UG']

    g2p_genie = pd.merge(g2p_grouped, genie, how='left',
                         right_on=['Chromosome', 'Start_Position', 'Reference_Allele', 'Tumor_Seq_Allele2'], 
                         left_on=['feature.chromosome', 'feature.start', 'feature.ref', 'feature.alt']).fillna('')

    g2p_genie_sensitive = g2p_genie[g2p_genie['response_type'].isin(['Responsive', 'Sensitivity', 'sensitive'])]

    all_d = list(g2p_genie_sensitive['CANCER_TYPE'].unique())
    all_diseases = list(g2p_genie_sensitive['ONCOTREE_CODE'].unique())

    all_biom = list(g2p_genie_sensitive['feature.biomarker_type'].unique())

    # create a hashmap of tumors with sensitivity describing their highest
    # level of evidence
    tums = {}
    for index, row in g2p_genie_sensitive.iterrows():
        samp = row['Tumor_Sample_Barcode']
        if samp in tums:
            prev_index = evidence_levels.index(tums[samp])
            this_index = evidence_levels.index(row['evidence_label'])
            if prev_index > this_index:
                tums[samp] = row['evidence_label']
        else:
            tums[samp] = row['evidence_label']

    prop_sens = pd.DataFrame()
    for disease in all_d:
        # STACKED BARCHART
        tum_w_disease = g2p_genie[g2p_genie['CANCER_TYPE'].isin([disease])]
        t = len(list(tum_w_disease['Tumor_Sample_Barcode'].unique()))
        sens_tum_w_disease = g2p_genie_sensitive[g2p_genie_sensitive['CANCER_TYPE'].isin([disease])]
        s = len(list(sens_tum_w_disease['Tumor_Sample_Barcode'].unique()))
        p = s/t
        d = {'disease': disease, 'proportion': p}
        for level in evidence_levels:
            sens_w_disease_subl = sens_tum_w_disease[sens_tum_w_disease['evidence_label'].isin([level])]
            v = 'proportion_{}'.format(level)
            sens_tums = list(sens_w_disease_subl['Tumor_Sample_Barcode'].unique())
            for samp in sens_tums:
                if tums[samp] != level:
                    sens_w_disease_subl = sens_w_disease_subl[sens_w_disease_subl.Tumor_Sample_Barcode != samp]
            s = len(list(sens_w_disease_subl['Tumor_Sample_Barcode'].unique()))
            p = s/t
            d[v] = p
        prop_sens = prop_sens.append(d, ignore_index=True)

        #HEATMAP
        for bio in all_biom:
            bstd = sens_tum_w_disease[sens_tum_w_disease['feature.biomarker_type'].isin([bio])]
            d = {'disease': disease, 'biomarker': bio, 'num_samps': len(bstd)}


    prop_sens = prop_sens.sort_values(by=['proportion'], ascending=False).reset_index(drop=True)

    data = []
    for level in evidence_levels:
        data.append(go.Bar(x=prop_sens['disease'], y=prop_sens['proportion_{}'.format(level)], name=level))

    layout = go.Layout(
        title = 'CGI: Proportion of GENIE tumors with drug sensitivity',
        xaxis={
            'title': 'Cancers in GENIE with evidence in G2P of sensitivity to at least one drug'
        },
        yaxis={
            'title': 'Percent of total tumors of each cancer type with evidence of sensitivity'
        },
        width=5500,
        height=600,
        barmode='stack'
    )
    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename='cgi_proportion_drug_sensitivity_by_cancer')











