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


class Harmonizations(object):
    def __init__(self, es_host, index='associations'):
        self.db = G2PDatabase(es_host, index)

    def harmonization_counts(self):
        """ get raw counts and percentages """
        harmonization_counts_df = self.db.harmonization_counts()
        counts = pd.pivot_table(harmonization_counts_df,
                                index=['source'],
                                values=['value'],
                                columns=['aggregation_name'],
                                fill_value=0)
        counts.loc[:, ('value', 'harmonized_biomarkers_percent')] = 100 * counts['value']['harmonized_biomarkers'] / (counts['value']['harmonized_biomarkers'] + counts['value']['unharmonized_biomarkers'])  # NOQA
        counts.loc[:, ('value', 'harmonized_phenotype_percent')] = 100 * counts['value']['harmonized_phenotype'] / (counts['value']['harmonized_phenotype'] + counts['value']['unharmonized_phenotype'])  # NOQA
        counts.loc[:, ('value', 'harmonized_environment_percent')] = 100 * counts['value']['harmonized_environment'] / (counts['value']['harmonized_environment'] + counts['value']['unharmonized_environment'])  # NOQA
        counts.loc[:, ('value', 'harmonized_features_percent')] = 100 * counts['value']['harmonized_features'] / (counts['value']['harmonized_features'] + counts['value']['unharmonized_features'])  # NOQA
        return counts

    def harmonization_percentages(self):
        """filter out only percentages """
        counts = self.harmonization_counts()
        stacked = pd.DataFrame(counts.stack().to_records()).set_index('source')
        stacked = stacked[stacked.aggregation_name.str.match('.*percent')]
        percentages = pd.pivot_table(stacked,
                                     index=['source'],
                                     values=['value'],
                                     columns=['aggregation_name'],
                                     fill_value=0)
        return percentages

    def harmonization_percentages_figure(self, path=None):
        """ draw the figure for percentages """
        # Draw a heatmap with the numeric values in each cell
        percentages = self.harmonization_percentages()
        sns.set(font_scale=1.5)
        fig, ax = plt.subplots(figsize=(18, 12))
        xticklabels = ['biomarkers','environment',  'features', 'phenotype']
        sns.heatmap(percentages, fmt="1.2f", linewidths=.5, ax=ax, cbar=False,
                    cmap="YlGnBu", annot=True, vmax=100,
                    xticklabels=xticklabels)
        ax.set_xlabel('harmonization %')
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
    print 'producing harmonization_percentages.'
    harmonizations = Harmonizations(es_host=args.host, index=args.index)
    harmonizations.harmonization_percentages_figure(path='./images/harmonization_percentages.png')
