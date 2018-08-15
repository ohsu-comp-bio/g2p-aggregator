# import litvar extract


import json
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import nltk

# create list of summary counts for each PMID
counts = []
# property names
concepts = ['chemicals', 'diseases', 'genes', 'variants']

# create list of verbs used in description
description_verbs = []

# load summary created from g2p 
def load():
    with open("litvar_analysis.json", "r") as ins:
        content = ins.readlines()
        counts = json.loads(content[0])
        description_verbs = json.loads(content[1])
    return counts, description_verbs 
    

# Publications mentioning specific variants
def genes_only_vs_has_variants(counts):
    no_variants = list(filter(lambda c: c['variants'] == 0, counts))
    has_variants = list(filter(lambda c: c['variants'] > 0, counts))
    plt.pie([len(no_variants), len(has_variants)], labels=['genes_only', 'variants'])
    plt.show()
    

# Publications mentioning specific variants
def singular_vs_plural_evidence(counts):
    def is_singular(c):
        return c['variants'] < 2 and c['diseases'] < 2 and  c['genes'] < 2
    singular = list(filter(lambda c: is_singular(c), counts))
    plural = list(filter(lambda c: not is_singular(c), counts))
    plt.pie([len(singular), len(plural)], labels=['singular', 'plural'])
    plt.show()
    

#  Correlate variant to disease counts
def plot_variant_by_disease(counts):
    plt.figure(figsize=(10, 8))
    df = pd.DataFrame.from_records(counts)
    variants = df['variants']
    diseases = df['diseases']
    ids = df['_id']
    df=pd.DataFrame({'variant': variants, 'disease': diseases, 'id': ids })
    df_wide=df.pivot_table( index='variant', columns='disease', values='id' )
    variant_to_disease_counts=sns.heatmap( df_wide, cbar=False)
    plt.show(variant_to_disease_counts)


# Correlate publication concept counts
def publication_concepts_scatter(counts):
    df = pd.DataFrame.from_records(counts)
    df = df.set_index('_id')
    sns.pairplot(df, kind="scatter")
    plt.show()


# Most commonly used description verbs
def top_verbs(description_verbs, size=50):    
    plt.figure(figsize=(10, 8))
    fdist1 = nltk.FreqDist(description_verbs)
    fdist1.plot(size, cumulative=False)

def top_verbs_table(description_verbs, size=50):    
    plt.figure(figsize=(10, 8))
    fdist1 = nltk.FreqDist(description_verbs)
    fdist1.tabulate(size, cumulative=False)