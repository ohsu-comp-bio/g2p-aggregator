
# pip install matplotlib
# pip install qgrid
# jupyter nbextension enable --py --sys-prefix widgetsnbextension
# jupyter nbextension enable --py --sys-prefix qgrid

# see https://github.com/quantopian/qgrid#jupyterlab-installation

# for reporting
import pandas as pd
import numpy as np
from collections import Counter
import datetime


# for displays and interactivity
import matplotlib.pyplot as plt
import qgrid
from IPython.display import Javascript
from IPython.display import display, Markdown  
from IPython.display import clear_output
from ipywidgets import VBox, HTML
import ipywidgets as widgets
from collections import Counter
import urllib.parse

query_names = ['alleles', '~location', '~range', 'protein_effects', 'protein_domains', '~biomarker_type', 'genes', 'pathways']

evidence_levels = ['A', 'B', 'C', 'D']

def collect(s, md=None):
    try:
        s = s.decode() 
    except AttributeError:
        pass
    if md:
        md = u'{}\n{}'.format(md, s)
    else:
        md = u'{}'.format(s)
    return md

class Explorer:
    
    def __init__(self, queries_p, datasets_p, summary_p):
        self.allele = self.summary_widget = self.toggles = self.vbox = None
        self.queries =  self.datasets = self.summary = self.detail_widget = self.publications = None
        self.html = HTML('')
        self.queries = queries_p
        self.datasets = datasets_p
        self.summary = summary_p
        self.top3 = HTML('')
        self.publication_iframe = HTML('')
        self.query_string = None
        


        
    def top(self, df, fields = [ 'genes', 'publications', 'evidence_label', 'phenotypes', 'drugs' ], size=3):
        counters = {}
        for f in fields:
            counters[f] = []
            counter = Counter()
            for value in df[f]:
                if isinstance(value, (list,tuple,)):
                    for v in value:
                        counter[v] += 1
                else:
                    counter[value] += 1
            for c in counter.most_common(size):
                counters[f].append({'value': c[0], 'count': c[1]})
        return counters    

    def format_top3(self, df, label):
        counters = self.top(df)
        heading = HTML('<h4>Summary Counts</h4>')

        md = 'Most frequently mentioned: <br/>'.format(self.allele,label)
        for c in ['phenotypes','genes','drugs','publications','evidence_label']:
            md = collect('<b>  * {}:</b>'.format(c), md)
            a = []
            for v in counters[c]:
                a.append('{} ({})'.format(v['value'], v['count'] ))
            md = collect('{}. <br/>'.format(a), md)                

        md += '<h6><a href="https://dms-dev.compbio.ohsu.edu/#{}"  target="_blank">explore more for allele:{} query:{}" <img src="https://www.freeiconspng.com/uploads/16x16-download-link-icon-11.png" width="16" alt="off-screen" /></a></h6>'.format(urllib.parse.quote(self.query_string), self.allele,label)
        
        self.top3 = VBox(children=[HTML(md)]) # heading, counters_grid, 
    
    def display_df(self, df, observer=None):
        """ display any dataframe """
        df_widget = qgrid.show_grid(df, grid_options={'editable':False})
        if observer:
            df_widget.observe(observer, names=['_selected_rows'])   # ,  
        return df_widget


    def select_detail_row(self, widget, change):
        selected_row = widget.get_selected_df().to_dict('records')[0]
        self.publications = selected_row['publications']
        for publication in self.publications.split(","):
            try:
                self.publication_iframe = HTML('<p>{}</p><iframe src="{}" height="900" width="900"></iframe>'.format(selected_row['description'], publication))
            except Exception as e:
                print(e)
                raise e
        self.vbox.children = [self.summary_widget,
          self.html,
          self.toggles,
          self.top3,
          self.detail_widget,
          self.publication_iframe
         ]
        
    

    def toggle_click(self, change):
        df = self.datasets[self.allele][change['new']]
        for q in self.queries:
            if q['allele'] == self.allele and q['name'] == change['new']:
                self.query_string = q['query_string']
        self.format_top3(df, label=change['new'])
        self.publication_iframe = HTML('')
        self.publications = None
        self.detail_widget = self.display_df(df, lambda  change: self.select_detail_row(self.detail_widget, change))        
        self.vbox.children = [self.summary_widget,
                              self.html,
                              self.toggles,
                              self.top3,
                              self.detail_widget,
                              self.publication_iframe
                             ]
    

    def select_summary_row(self, widget, change):
        try:
            selected_row = widget.get_selected_df().to_dict('records')[0]
            self.allele = selected_row['allele']
            keys = []
            for k in query_names:
                if k in self.datasets[self.allele] and len(self.datasets[self.allele][k]):
                    keys.append(k)
                    # children.append(display_df(datasets[allele][k]))
            self.toggles = widgets.ToggleButtons(
                options=keys,
                description='Query:',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                # tooltips=['Description of slow', 'Description of regular', 'Description of fast'],
                #     icons=['check'] * 3
            )

            self.toggles.observe(self.toggle_click, 'value')
            self.html.value = '<h4>{}</h4> '.format(self.allele)
            self.publication_iframe = HTML('')            
            children = [widget, self.html]
            if len(keys) > 0:
                df = self.datasets[self.allele][keys[0]]                 
                self.detail_widget = self.display_df(df, lambda  change: self.select_detail_row(self.detail_widget, change))
                for q in self.queries:
                    if q['allele'] == self.allele and q['name'] == keys[0]:
                        self.query_string = q['query_string']
                
                self.format_top3(df, label=keys[0])
                children = [widget, self.html, self.toggles, self.top3, self.detail_widget, self.publication_iframe]
            self.vbox.children = children
        except Exception as e:
            print(e)
            raise e            
    
    def explore(self):
        try:
            self.summary_widget = self.display_df(self.summary, lambda  change: self.select_summary_row(self.summary_widget, change) )
            self.vbox = VBox(children=[self.summary_widget,self.html])
            display(self.vbox)
        except Exception as e:
            print(e)
            raise     
            

    def report(self, dataset_name):
        # maximum number of matching evidence items
        limit = 2

        def top(df, fields = ['genes', 'publications', 'evidence_label', 'phenotypes', 'drugs' ], size=3):
            counters = []
            for f in fields:
                counter = Counter()
                for value in df[f]:
                    if isinstance(value, (list,tuple,)):
                        for v in value:
                            counter[v] += 1
                    else:
                        counter[value] += 1
                for c in counter.most_common(size):
                    v = c[0]
                    counters.append({'field': f, 'value': v, 'count': c[1]})
            if len(counters) == 0:
                counters.append({'field': fields, 'value': None, 'count': None})
            return counters    

        md = collect('# {}'.format(dataset_name))

        
        md = collect('\n## Gene Centric\n_____', md)

        for name in query_names:
            df = pd.DataFrame()
            for allele in self.datasets.keys():
                if name in self.datasets[allele] and len(self.datasets[allele][name]):
                    df = df.append(self.datasets[allele][name])
            if len(df) == 0:
                continue
                
            md = collect('\n### {}\n'.format(name), md)
            for evidence_level in evidence_levels:
                evidence_level_df = df[df.evidence_label == evidence_level]
                if len(evidence_level_df):
                    gene = top(evidence_level_df, fields=['genes'], size=1)[0]['value']
                    md = collect('  * {} {}'.format(evidence_level, gene), md)
                    c = 0
                    for evidence in evidence_level_df.to_records():
                        if gene in evidence.genes:
                            md = collect('    * {} {} {}'.format(evidence.source,
                                                                 evidence.phenotypes,
                                                                 evidence.drugs), md)
                            md = collect('      * {}'.format(evidence.description), md)
#                             md = collect('      * {}'.format(evidence.matches), md)                   
                            md = collect('      * {}'.format(evidence.publications), md)                    
 
                            c += 1
                            if c == limit:
                                break

        
        
        md = collect('\n## Drug Centric\n_____', md)

        for name in query_names:
            df = pd.DataFrame()
            for allele in self.datasets.keys():
                if name in self.datasets[allele] and len(self.datasets[allele][name]):
                    df = df.append(self.datasets[allele][name])
            if len(df) == 0:
                continue
                
            md = collect('\n### {}\n'.format(name), md)
            for evidence_level in evidence_levels:
                evidence_level_df = df[df.evidence_label == evidence_level]
                if len(evidence_level_df):
                    drug = top(evidence_level_df, fields=['drugs'], size=1)[0]['value']
                    md = collect('  * {} {}'.format(evidence_level, drug), md)
                    c = 0
                    for evidence in evidence_level_df.to_records():
                        if drug in evidence.drugs:
                            md = collect('    * {} {} {}'.format(evidence.source,
                                                                 evidence.phenotypes ,
                                                                 evidence.drugs), md)
                            md = collect('      * {}'.format(evidence.description), md)
#                             md = collect('      * {}'.format(evidence.matches), md)                   
                            md = collect('      * {}'.format(evidence.publications), md)                    
 
                            c += 1
                            if c == limit:
                                break

        md = collect('\n## Phenotype Centric\n_____', md)

        for name in query_names:
            df = pd.DataFrame()
            for allele in self.datasets.keys():
                if name in self.datasets[allele] and len(self.datasets[allele][name]):
                    df = df.append(self.datasets[allele][name])
            if len(df) == 0:
                continue
            md = collect('\n### {}\n'.format(name), md)
            for evidence_level in evidence_levels:
                evidence_level_df = df[df.evidence_label == evidence_level]
                if len(evidence_level_df):
                    phenotype = top(evidence_level_df, fields=['phenotypes'], size=1)[0]['value']
                    md = collect('  * {} {}'.format(evidence_level, phenotype), md)
                    c = 0
                    for evidence in evidence_level_df.to_records():
                        if phenotype in evidence.phenotypes:
                            md = collect('    * {} {} {}'.format(evidence.source,
                                                                 evidence.phenotypes,
                                                                 evidence.drugs), md)
                            md = collect('      * {}'.format(evidence.description), md)
#                             md = collect('      * {}'.format(evidence.matches), md)                   
                            md = collect('      * {}'.format(evidence.publications), md)                    
 
                            c += 1
                            if c == limit:
                                break

        md = collect('\n## Publication Centric\n_____', md)

        for name in query_names:
            df = pd.DataFrame()
            for allele in self.datasets.keys():
                if name in self.datasets[allele] and len(self.datasets[allele][name]):
                    df = df.append(self.datasets[allele][name])
            if len(df) == 0:
                continue
            md = collect('\n### {}\n'.format(name), md)
            for evidence_level in evidence_levels:
                evidence_level_df = df[df.evidence_label == evidence_level]
                if len(evidence_level_df):
                    publication = top(evidence_level_df, fields=['publications'], size=1)[0]['value']
                    md = collect('  * {} {}'.format(evidence_level, publication), md)
                    c = 0
                    for evidence in evidence_level_df.to_records():
                        if publication in evidence.publications:
                            md = collect('    * {} {} {}'.format(evidence.source,
                                                                 evidence.phenotypes,
                                                                 evidence.drugs), md)
                            md = collect('      * {}'.format(evidence.description), md)
#                             md = collect('      * {}'.format(evidence.matches), md)                   
                            md = collect('      * {}'.format(evidence.publications), md)                    
                            c += 1
                            if c == limit:
                                break



        # print md    
        display(Markdown(md))
