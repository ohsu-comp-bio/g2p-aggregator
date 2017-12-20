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


class Overlaps(object):
    def __init__(self, es_host, index='associations'):
        self.db = G2PDatabase(es_host, index)
        self.index = index

    def feature_overlaps(self):
        """ determine feature overlaps % """

        def feature_hash(f):
            """ given a feature, hash it"""
            a = []
            for p in ['referenceName', 'chromosome', 'start',
                      'end', 'ref', 'alt']:
                a.append(str(getattr(f, p, '')))
            return ''.join(a)

        def aggregate_hit(o, hit):
            """ create a list of feature hashes"""
            if hit.source not in o:
                o[hit.source] = {'features': []}
            o[hit.source]['features'].extend([feature_hash(f)
                                              for f in hit.features])

        #  Use DSL to query genomic location, subset of fields
        s = Search(using=self.db.client, index=self.index) \
            .params(size=1000) \
            .query("query_string", query="_exists_:features.referenceName") \
            .source(includes=['source', 'features.referenceName',
                              'features.chromosome', 'features.start',
                              'features.end', 'features.ref', 'features.alt'])

        # create a {source:<name> , features:[<hashed>]}
        aggregate_hits = {}
        for hit in s.scan():
            aggregate_hit(aggregate_hits, hit)
        for k in aggregate_hits.keys():
            aggregate_hits[k]['features'] = list(
                                            set(aggregate_hits[k]['features']))
        total = 0
        for k in aggregate_hits.keys():
            total = total + len(aggregate_hits[k]['features'])

        # xform aggregate_hits to a dataframe
        features = pd.DataFrame([{'source': k, 'features': list(aggregate_hits[k]['features'])} for k in aggregate_hits]).set_index('source')  # NOQA

        # lightweight class
        Overlap = namedtuple('Overlap', ['other', 'source', 'size', 'percentage', 'other_size', 'source_size', 'other_features'])  # NOQA

        # intersection
        def features_intersection(df1, df2):
            return set(df1.features) & set(df2.features)

        # comparison of source to all other sources
        def source_intersection(source):
            others = set(features.index.tolist()) - set([source])
            for other in others:
                overlap_size = len(features_intersection(features.loc[source], features.loc[other]))
                other_size = len(features.loc[other].features)
                yield Overlap(other=other,
                              source=source,
                              size=overlap_size,
                              other_size=other_size,
                              source_size=len(features.loc[source].features),
                              percentage=(overlap_size / other_size) * 100,
                              other_features=set(features.loc[other].features)
                              )

        overlaps = []  # for plotting
        print('overall overlap')
        for source in features.index.tolist():
            total = set()
            for overlap in source_intersection(source):
                overlaps.append(overlap)  # for plotting
                total |= overlap.other_features  # for overall
                print('        {} {}/{} ({:.2f}%) overlap with {}'.format(source, overlap.size,
                                                                           overlap.other_size,
                                                                           overlap.percentage,
                                                                           overlap.other))
            overall = set(features.loc[source].features) & total
            print('  {}: {}/{} ({:.2f}%)'.format(source, len(overall), len(total), len(overall) / len(total)* 100))
        overlaps_df = pd.DataFrame(overlaps).pivot("source", "other", "percentage")
        return overlaps_df

    def feature_overlaps_figure(self, path=None):
        """ draw the figure for percentages """
        # Draw a heatmap with the numeric values in each cell
        overlaps_hm = self.feature_overlaps()
        sns.set(font_scale=1.5)
        # Draw a heatmap with the numeric values in each cell
        fig, ax = plt.subplots(figsize=(18, 12))
        sns.heatmap(overlaps_hm, annot=True, fmt="1.0f", linewidths=.5, ax=ax, cbar=False, cmap="YlGnBu",linecolor='black')
        if path:
            fig.savefig(path, bbox_inches='tight')

        return fig

    def publication_overlaps(self):
        """ determine publication overlaps % """

        def aggregate_hit(o, hit):
            """ create a list of publication hashes"""
            if hit.source not in o:
                o[hit.source] = {'publications': []}
            publications = []
            for e in hit.association.evidence:
                    for p in e.info.publications:
                        publications.append(p)
            o[hit.source]['publications'].extend(publications)

        #  Use DSL to query evidence, subset of fields
        s = Search(using=self.db.client, index=self.index) \
          .params(size=1000) \
          .query("query_string", query="_exists_:association.evidence.info.publications") \
          .source(includes=['source', 'association.evidence.info.publications'])

        # create a {source:<name> , publications:[<hashed>]}
        aggregate_hits = {}
        for hit in s.scan():
            aggregate_hit(aggregate_hits, hit)
        for k in aggregate_hits.keys():
            aggregate_hits[k]['publications'] = list(
                                            set(aggregate_hits[k]['publications']))
        total = 0
        for k in aggregate_hits.keys():
            total = total + len(aggregate_hits[k]['publications'])

        #  xform aggregate_hits to a dataframe
        publications = pd.DataFrame([{'source':k, 'publications':list(aggregate_hits[k]['publications'])} for k in aggregate_hits]).set_index('source')

        # lightweight class
        Overlap = namedtuple('Overlap', ['other', 'source', 'size', 'percentage', 'other_size', 'source_size',
                                         'other_publications' ])

        # intersection
        def publications_intersection(df1, df2):
            return set(df1.publications) & set(df2.publications)

        # comparison of source to all other sources
        def source_intersection(source):
            others = set(publications.index.tolist()) - set([source])
            for other in others:
                overlap_size = len(publications_intersection(publications.loc[source], publications.loc[other]))
                other_size = len(publications.loc[other].publications)
                yield Overlap(other=other,
                              source=source,
                              size=overlap_size,
                              other_size=other_size,
                              source_size=len(publications.loc[source].publications),
                              percentage=(overlap_size / other_size) * 100,
                              other_publications=set(publications.loc[other].publications)
                             )

        overlaps = [] # for plotting
        print('overall overlap')
        for source in publications.index.tolist():
            total = set()
            for overlap in source_intersection(source):
                overlaps.append(overlap)  # for plotting
                total |= overlap.other_publications  # for overall
                print('        {} {}/{} ({:.2f}%) overlap with {}'.format(source, overlap.size,
                                                                           overlap.other_size,
                                                                           overlap.percentage,
                                                                           overlap.other))
            overall = set(publications.loc[source].publications) & total
            print('  {}: {}/{} ({:.2f}%)'.format(source, len(overall), len(total), len(overall) / len(total)* 100))


        overlaps_df = pd.DataFrame(overlaps).pivot("source", "other", "percentage")
        return overlaps_df

    def publication_overlaps_figure(self, path=None):
        """ draw the figure for percentages """
        # Draw a heatmap with the numeric values in each cell
        overlaps_hm = self.publication_overlaps()
        sns.set(font_scale=1.5)
        # Draw a heatmap with the numeric values in each cell
        fig, ax = plt.subplots(figsize=(18, 12))
        sns.heatmap(overlaps_hm, annot=True, fmt="1.0f", linewidths=.5, ax=ax, cbar=False, cmap="YlGnBu",linecolor='black')
        if path:
            fig.savefig(path, bbox_inches='tight')

        return fig

    def environment_overlaps(self):
        """ determine environment overlaps % """

        def aggregate_hit(o, hit):
            """ create a list of environment hashes"""
            if hit.source not in o:
                o[hit.source] = {'environments': []}
            environments = []
            for ec in hit.association.environmentalContexts:
              environments.append(ec['id'])
            o[hit.source]['environments'].extend(environments)

        #  Use DSL to query evidence, subset of fields
        s = Search(using=self.db.client, index=self.index) \
          .params(size=1000) \
          .query("query_string", query="+association.environmentalContexts.id:*") \
          .source(includes=['source', 'association.environmentalContexts.id'])

        # create a {source:<name> , environments:[<hashed>]}
        aggregate_hits = {}
        for hit in s.scan():
            aggregate_hit(aggregate_hits, hit)
        for k in aggregate_hits.keys():
            aggregate_hits[k]['environments'] = list(
                                            set(aggregate_hits[k]['environments']))
        total = 0
        for k in aggregate_hits.keys():
            total = total + len(aggregate_hits[k]['environments'])

        #  xform aggregate_hits to a dataframe
        environments = pd.DataFrame([{'source':k, 'environments':list(aggregate_hits[k]['environments'])} for k in aggregate_hits]).set_index('source')

        # lightweight class
        Overlap = namedtuple('Overlap', ['other', 'source', 'size', 'percentage', 'other_size', 'source_size',
                                         'other_environments' ])

        # intersection
        def environments_intersection(df1, df2):
            return set(df1.environments) & set(df2.environments)

        # comparison of source to all other sources
        def source_intersection(source):
            others = set(environments.index.tolist()) - set([source])
            for other in others:
                overlap_size = len(environments_intersection(environments.loc[source], environments.loc[other]))
                other_size = len(environments.loc[other].environments)
                yield Overlap(other=other,
                              source=source,
                              size=overlap_size,
                              other_size=other_size,
                              source_size=len(environments.loc[source].environments),
                              percentage=(overlap_size / other_size) * 100,
                              other_environments=set(environments.loc[other].environments)
                             )

        overlaps = [] # for plotting
        print('overall overlap')
        for source in environments.index.tolist():
            total = set()
            for overlap in source_intersection(source):
                overlaps.append(overlap)  # for plotting
                total |= overlap.other_environments  # for overall
                print('        {} {}/{} ({:.2f}%) overlap with {}'.format(source, overlap.size,
                                                                           overlap.other_size,
                                                                           overlap.percentage,
                                                                           overlap.other))
            overall = set(environments.loc[source].environments) & total
            print('  {}: {}/{} ({:.2f}%)'.format(source, len(overall), len(total), len(overall) / len(total)* 100))


        overlaps_df = pd.DataFrame(overlaps).pivot("source", "other", "percentage")
        return overlaps_df

    def environment_overlaps_figure(self, path=None):
        """ draw the figure for percentages """
        # Draw a heatmap with the numeric values in each cell
        overlaps_hm = self.environment_overlaps()
        sns.set(font_scale=1.5)
        # Draw a heatmap with the numeric values in each cell
        fig, ax = plt.subplots(figsize=(18, 12))
        sns.heatmap(overlaps_hm, annot=True, fmt="1.0f", linewidths=.5, ax=ax, cbar=False, cmap="YlGnBu",linecolor='black')
        if path:
            fig.savefig(path, bbox_inches='tight')

        return fig

    def phenotype_overlaps(self):
        """ determine phenotype overlaps % """

        def aggregate_hit(o, hit):
            """ create a list of phenotype hashes"""
            if hit.source not in o:
                o[hit.source] = {'phenotypes': []}
            o[hit.source]['phenotypes'].extend(hit.association.phenotype.type.id)

        #  Use DSL to query evidence, subset of fields
        s = Search(using=self.db.client, index=self.index) \
          .params(size=1000) \
          .query("query_string", query="+association.phenotype.type.id:*") \
          .source(includes=['source', 'association.phenotype.type.id'])

        # create a {source:<name> , phenotypes:[<hashed>]}
        aggregate_hits = {}
        for hit in s.scan():
            aggregate_hit(aggregate_hits, hit)
        for k in aggregate_hits.keys():
            aggregate_hits[k]['phenotypes'] = list(
                                            set(aggregate_hits[k]['phenotypes']))
        total = 0
        for k in aggregate_hits.keys():
            total = total + len(aggregate_hits[k]['phenotypes'])

        #  xform aggregate_hits to a dataframe
        phenotypes = pd.DataFrame([{'source':k, 'phenotypes':list(aggregate_hits[k]['phenotypes'])} for k in aggregate_hits]).set_index('source')

        # lightweight class
        Overlap = namedtuple('Overlap', ['other', 'source', 'size', 'percentage', 'other_size', 'source_size',
                                         'other_phenotypes' ])

        # intersection
        def phenotypes_intersection(df1, df2):
            return set(df1.phenotypes) & set(df2.phenotypes)

        # comparison of source to all other sources
        def source_intersection(source):
            others = set(phenotypes.index.tolist()) - set([source])
            for other in others:
                overlap_size = len(phenotypes_intersection(phenotypes.loc[source], phenotypes.loc[other]))
                other_size = len(phenotypes.loc[other].phenotypes)
                yield Overlap(other=other,
                              source=source,
                              size=overlap_size,
                              other_size=other_size,
                              source_size=len(phenotypes.loc[source].phenotypes),
                              percentage=(overlap_size / other_size) * 100,
                              other_phenotypes=set(phenotypes.loc[other].phenotypes)
                             )

        overlaps = [] # for plotting
        print('overall overlap')
        for source in phenotypes.index.tolist():
            total = set()
            for overlap in source_intersection(source):
                overlaps.append(overlap)  # for plotting
                total |= overlap.other_phenotypes  # for overall
                print('        {} {}/{} ({:.2f}%) overlap with {}'.format(source, overlap.size,
                                                                           overlap.other_size,
                                                                           overlap.percentage,
                                                                           overlap.other))
            overall = set(phenotypes.loc[source].phenotypes) & total
            print('  {}: {}/{} ({:.2f}%)'.format(source, len(overall), len(total), len(overall) / len(total)* 100))


        overlaps_df = pd.DataFrame(overlaps).pivot("source", "other", "percentage")
        return overlaps_df

    def phenotype_overlaps_figure(self, path=None):
        """ draw the figure for percentages """
        # Draw a heatmap with the numeric values in each cell
        overlaps_hm = self.phenotype_overlaps()
        sns.set(font_scale=1.5)
        # Draw a heatmap with the numeric values in each cell
        fig, ax = plt.subplots(figsize=(18, 12))
        sns.heatmap(overlaps_hm, annot=True, fmt="1.0f", linewidths=.5, ax=ax, cbar=False, cmap="YlGnBu",linecolor='black')
        if path:
            fig.savefig(path, bbox_inches='tight')

        return fig

    def gene_overlaps(self):
        """ determine gene overlaps % """

        # Use DSL to aggregate counts on the server
        s = Search(using=self.db.client, index=self.index)
        # limit query to 1K sources, 1M genes each
        s.aggs.bucket('source', 'terms', field='source.keyword', size=1000) \
              .bucket('genes', 'terms',field='genes.keyword', size=1000000)
        aggregation = s.execute()
        # Create dataframe to hold results
        gene_counts = pd.DataFrame([ {'source':source.key,
                             'evidence_count': source.doc_count,
                             'genes_count': len(source.genes.buckets),
                             'genes':[ {'gene': gene.key, 'count': gene.doc_count}
                                for gene in source.genes.buckets
                             ],
                             'gene_names': [gene.key for gene in source.genes.buckets]
                            }
                            for source in aggregation.aggregations.source.buckets])
        gene_counts = gene_counts.set_index('source')
        gene_counts[['evidence_count', 'genes_count', 'genes','gene_names']]
        # lightweight class
        Overlap = namedtuple('Overlap', ['other', 'source', 'size', 'percentage', 'other_size', 'source_size',
                                         'other_gene_names' ])

        # intersection
        def genes_intersection(df1, df2):
            return set(df1.gene_names) & set(df2.gene_names)

        # comparison of source to all other sources
        def source_intersection(source):
            others = set(gene_counts.index.tolist()) - set([source])
            for other in others:
                overlap_size = len(genes_intersection(gene_counts.loc[source], gene_counts.loc[other]))
                other_size = len(gene_counts.loc[other].gene_names)
                yield Overlap(other=other,
                              source=source,
                              size=overlap_size,
                              other_size=other_size,
                              source_size=len(gene_counts.loc[source].gene_names),
                              percentage=(overlap_size / other_size) * 100,
                              other_gene_names=set(gene_counts.loc[other].gene_names)
                             )

        overlaps = [] # for plotting
        print('overall overlap')
        for source in gene_counts.index.tolist():
            total = set()
            for overlap in source_intersection(source):
                overlaps.append(overlap)  # for plotting
                total |= overlap.other_gene_names  # for overall
                print('    {} {}/{} ({:.2f}%) overlap with {}'.format(source, overlap.size,
                                                                   overlap.other_size,
                                                                   overlap.percentage,
                                                                   overlap.other))
            overall = set(gene_counts.loc[source].gene_names) & total
            print('  {}: {}/{} ({:.2f}%)'.format(source, len(overall), len(total), len(overall) / len(total)* 100))


        overlaps_df = pd.DataFrame(overlaps).pivot("source", "other", "percentage")
        return overlaps_df

    def gene_overlaps_figure(self, path=None):
        """ draw the figure for percentages """
        # Draw a heatmap with the numeric values in each cell
        overlaps_hm = self.gene_overlaps()
        sns.set(font_scale=1.5)
        # Draw a heatmap with the numeric values in each cell
        fig, ax = plt.subplots(figsize=(18, 12))
        sns.heatmap(overlaps_hm, annot=True, fmt="1.0f", linewidths=.5, ax=ax, cbar=False, cmap="YlGnBu",linecolor='black')
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
    print 'producing feature_overlaps_figure, may take several minutes.'
    overlaps = Overlaps(es_host=args.host, index=args.index)
    overlaps.feature_overlaps_figure(path='./images/feature_overlaps.png')
    print 'producing publication_overlaps_figure, may take several minutes.'
    overlaps.publication_overlaps_figure(path='./images/publication_overlaps.png')
    print 'producing environment_overlaps_figure, may take several minutes.'
    overlaps.publication_overlaps_figure(path='./images/environment_overlaps.png')
    print 'producing phenotype_overlaps_figure, may take several minutes.'
    overlaps.phenotype_overlaps_figure(path='./images/phenotype_overlaps.png')
    print 'producing genes_overlaps_figure, may take several minutes.'
    overlaps.gene_overlaps_figure(path='./images/gene_overlaps.png')
