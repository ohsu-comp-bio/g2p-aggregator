'''
OncoKB Paper Application
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
ONCOKB_PATIENTS = '../../data/msk_impact_2017/data_clinical_patient.txt'
ONCOKB_SAMPLES = '../../data/msk_impact_2017/data_clinical_sample.txt'
ONCOKB_MUTS = '../../data/msk_impact_2017/data_mutations_uniprot.txt'
evidence_levels = ['A', 'B', 'C', 'D']
evidence_levels_okb = ['A', 'B', 'C', 'D', 'Other']


def pie_chart(df, title, filename):
    data = []
    for level in evidence_levels_okb:
        data.append(len(df[df['evidence_label'].isin([level])]))
    fig = { 'data': [{
              'labels': evidence_levels_okb,
              'values': data,
              'type': 'pie'
            }],
            'layout' : {
              'title': title
            }
          }
    plotly.offline.plot(fig, filename=filename)


if __name__ == '__main__':
    site = G2PDatabase(HOST)
    g2p = site.associations_dataframe()
    g2p = g2p.fillna('')

    okb_patients = pd.read_csv(ONCOKB_PATIENTS, sep='\t', comment='#')
    okb_samples = pd.read_csv(ONCOKB_SAMPLES, sep='\t', comment='#')
    okb_muts = pd.read_csv(ONCOKB_MUTS, sep='\t', comment='#')

    okb = pd.merge(okb_patients, okb_samples, left_on=['PATIENT_ID'], right_on=['PATIENT_ID']).fillna(0)
    okb = pd.merge(okb, okb_muts, left_on=['SAMPLE_ID'], right_on=['Tumor_Sample_Barcode'])

    g2p_okb = pd.merge(okb, g2p, how='left',
                       left_on=['Chromosome', 'Start_Position', 'Reference_Allele', 'Tumor_Seq_Allele2'],
                       right_on=['feature.chromosome', 'feature.start', 'feature.ref', 'feature.alt']).fillna('Other')

    # OncoKB only evidence level pie chart comparison
    g2p_okb_only = g2p_okb[g2p_okb['source'].isin(['oncokb'])]
    title = 'Levels of evidence in Oncokb DataSet'
    filename = 'oncokb_levels_of_evidence'
    pie_chart(g2p_okb_only, title, filename)

    # Whole Dataset pie chart comparison
    title = 'Types of evidence in Oncokb DataSet compared with all G2P evidence'
    filename = 'oncokb_levels_of_evidence_g2p'
    pie_chart(g2p_okb, title, filename)


    # WOO!


    # Bar chart
    g2p_okb = g2p_okb[~(g2p_okb['ONCOTREE_CODE'].isin(['None', '']))]
    all_diseases = list(g2p_okb['ONCOTREE_CODE'].unique())
    print len(all_diseases)

    g2p_okb_ev = g2p_okb[g2p_okb['evidence_label'].isin(evidence_levels)]
    all_diseases = list(g2p_okb_ev['ONCOTREE_CODE'].unique())
    print len(all_diseases)

    # create a hashmap of tumors with sensitivity describing their highest
    # level of evidence
    tums = {}
    for index, row in g2p_okb_ev.iterrows():
        samp = row['Tumor_Sample_Barcode']
        if samp in tums:
            prev_index = evidence_levels_okb.index(tums[samp])
            this_index = evidence_levels_okb.index(row['evidence_label'])
            if prev_index > this_index:
                tums[samp] = row['evidence_label']
        else:
            tums[samp] = row['evidence_label']

    oncokb = pd.DataFrame()
    for disease in all_diseases:
        tum_w_disease = g2p_okb[g2p_okb['ONCOTREE_CODE'].isin([disease])]
        n = len(list(tum_w_disease['Tumor_Sample_Barcode'].unique()))
        tru_tum_w_disease = g2p_okb_ev[g2p_okb_ev['ONCOTREE_CODE'].isin([disease])]
        m = len(list(tru_tum_w_disease['Tumor_Sample_Barcode'].unique()))
        p = (m/n)*100
        d = {'disease': disease, 'total_percent': p}
        for level in evidence_levels:
            v = 'percent_{}'.format(level)
            tum_w_disease_lev = tru_tum_w_disease[tru_tum_w_disease['evidence_label'].isin([level])]
            samps = list(tum_w_disease_lev['Tumor_Sample_Barcode'].unique())
            for samp in samps:
                if tums[samp] != level:
                    tum_w_disease_lev = tum_w_disease_lev[tum_w_disease_lev.Tumor_Sample_Barcode != samp]
            s = len(list(tum_w_disease_lev['Tumor_Sample_Barcode'].unique()))
            p = (s/n)*100
            d[v] = p
        oncokb = oncokb.append(d, ignore_index=True)

    oncokb = oncokb.sort_values(by=['total_percent', 'percent_A', 'percent_B', 'percent_C', 'percent_D'],
                                ascending=False).reset_index(drop=True)

    data = []
    for level in evidence_levels:
        data.append(go.Bar(x=oncokb['disease'], y=oncokb['percent_{}'.format(level)], name=level))

    layout = go.Layout(
        title = 'Distribution of actionability by tumor type',
        xaxis = {
            'title': 'OncoKB cohort cancer type (ONCOTREE code)'
        },
        yaxis = {
            'title': 'Percent evidence of each evidence label'
        },
        width = 1300,
        height = 600,
        barmode = 'stack'
    )
    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename='oncokb_actionability_tumor_type')


