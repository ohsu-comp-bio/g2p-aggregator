
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from collections import OrderedDict
from itertools import product
import json
from pandas.io.json import json_normalize
import copy

import pandas as pd

CLIENT = Elasticsearch()
INDEX = 'associations'

EXPECTED_CGI_EVIDENCE_COUNT = 1072
EXPECTED_CGI_ONCOGENIC_EVIDENCE_COUNT = 301

EXPECTED_ONCOKB_EVIDENCE_COUNT = 4074
EXPECTED_ONCOKB_ONCGENIC_EVIDENCE_COUNT = 38


def test_cgi_evidence_counts():
    s = Search(using=CLIENT, index=INDEX)
    s = s.params(size=0)
    s = s.query("query_string", query="+source:cgi")
    s.aggs.bucket('cgi_count', 'terms', field='source.keyword')
    agg = s.execute().aggregations
    assert agg.cgi_count.buckets[0].doc_count == EXPECTED_CGI_EVIDENCE_COUNT


def test_cgi_oncogenic_evidence_counts():
    s = Search(using=CLIENT, index=INDEX)
    s = s.params(size=0)
    s = s.query("query_string", query='+source:cgi +association.oncogenic:"*oncogenic mutation"')
    s.aggs.bucket('cgi_count', 'terms', field='source.keyword')
    agg = s.execute().aggregations
    assert agg.cgi_count.buckets[0].doc_count == EXPECTED_CGI_ONCOGENIC_EVIDENCE_COUNT


def test_cgi_oncogenic_spotcheck_evidence_feature_counts():
    query = '+source:cgi +association.description:"[\'KRAS\'] BET inhibitors Responsive"'
    s = Search(using=CLIENT, index=INDEX)
    s = s.params(size=0)
    s = s.query("query_string", query=query)
    s.aggs.bucket('cgi_count', 'terms', field='source.keyword')
    agg = s.execute().aggregations
    assert agg.cgi_count.buckets[0].doc_count == 1

    s = Search(using=CLIENT, index=INDEX)
    s = s.params(size=1)
    s = s.query("query_string", query=query)
    result = s.execute()
    assert len(result.hits[0].features) == 14


def test_oncokb_evidence_counts():
    s = Search(using=CLIENT, index=INDEX)
    s = s.params(size=0)
    s = s.query("query_string", query="+source:oncokb")
    s.aggs.bucket('cgi_count', 'terms', field='source.keyword')
    agg = s.execute().aggregations
    assert agg.cgi_count.buckets[0].doc_count == EXPECTED_ONCOKB_EVIDENCE_COUNT


def test_oncokb_oncogenic_evidence_counts():
    s = Search(using=CLIENT, index=INDEX).source(includes=['oncokb'])
    s = s.query("query_string", query="+source:oncokb  ")
    # peek into opaque source to see if oncogenic feature
    hits = [hit for hit in s.scan() if 'Oncogenic Mutations' in hit.oncokb]
    assert len(hits) == EXPECTED_ONCOKB_ONCGENIC_EVIDENCE_COUNT


def test_oncokb_oncogenic_spotcheck_evidence_feature_counts():
    query = '+source:oncokb  +association.phenotype.type.id:"DOID\:9256" +association.publication_url.keyword:"http\://www.ncbi.nlm.nih.gov/pubmed/21228335"'
    s = Search(using=CLIENT, index=INDEX)
    s = s.params(size=0)
    s = s.query("query_string", query=query)
    s.aggs.bucket('oncokb_count', 'terms', field='source.keyword')
    agg = s.execute().aggregations
    assert agg.oncokb_count.buckets[0].doc_count == 1

    s = Search(using=CLIENT, index=INDEX)
    s = s.params(size=1)
    s = s.query("query_string", query=query)
    result = s.execute()
    assert len(result.hits[0].features) == 43
