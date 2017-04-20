import imp
import requests
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import json
ophion = imp.load_source('ophion_client', 'ophion/client/python/ophion.py')


es = Elasticsearch(
    ['10.96.11.130']  # '10.96.11.130'
)


def harvest(genes=['BRAF'], sample_limit=5):
    O = ophion.Ophion('http://bmeg.compbio.ohsu.edu')
    sample_count = 0
    summary = {}
    for gene in genes:
        gene_query = O.query() \
                      .has("gid", "gene:%s" % (gene))
        gene_result = gene_query.execute()['result']
        if (len(gene_result) == 0):
            continue
        if gene not in summary:
            summary[gene] = {'histologies':{}}
        samples_query = O.query().has("gid", "gene:%s" % (gene)) \
                                 .incoming("affectsGene") \
                                 .incoming("transcriptEffectOf") \
                                 .outgoing("annotationFor") \
                                 .outgoing("inCallSet") \
                                 .outgoing("callsFor")
        samples = samples_query.execute()['result']
        if (len(samples) == 0):
            continue

        for sample in samples:
            sample_count = sample_count + 1
            if sample_count > sample_limit:
                continue
            h = ','.join(json.loads(sample['properties']['info.histology']))
            if h not in summary[gene]['histologies']:
                summary[gene]['histologies'][h] = {'responseOf': {}}
            histology = summary[gene]['histologies'][h]
            response_curves_query = O.query() \
                          .has("gid", "%s" % (sample['properties']['gid'])) \
                          .incoming("responseOf")
            response_curves = response_curves_query.execute()['result']
            if (len(response_curves) == 0):
                continue
            for response_curve in response_curves:
                compounds_query = O.query() \
                              .has("gid", "%s" % (response_curve['properties']['gid'])) \
                              .outgoing("responseTo")
                compounds = compounds_query.execute()['result']
                if (len(compounds) == 0):
                    continue
                for compound in compounds:
                    compound_gid = compound['properties']['gid']
                    if 'summary' not in response_curve['properties']:
                        continue

                    for s in response_curve['properties']['summary']:
                        if compound_gid not in histology['responseOf']:
                            histology['responseOf'][compound_gid] = {}
                        compound_response = histology['responseOf'][compound_gid]
                        if s['type'] not in compound_response:
                            s['count'] = 0
                            s['sum'] = 0
                            s['avg'] = 0
                            compound_response[s['type']] = s
                        type_summary = compound_response[s['type']]
                        if 'value' in s:
                            type_summary['count'] = type_summary['count'] + 1
                            type_summary['sum'] = s['value'] + type_summary['sum']
                            type_summary['avg'] = type_summary['sum'] / type_summary['count']
                            del s['value']

                            # print compound_response

                    # g2p = {'gene': gene, 'source': 'bmeg'}
                    # bmeg = {'gene': gene_result[0],
                    #         'sample': sample,
                    #         'response_curve': response_curve,
                    #         'compound': compound,
                    #         }
                    # g2p['bmeg'] = bmeg
                    # result = es.index(index='genes2', body=g2p, doc_type='bmeg', op_type='index' )
                    # if result['_shards']['failed'] > 0:
                    #     print 'FAIL updating compound {}'.format(compound['properties']['gid'])
                    # else:
                    #     print 'OK updating compound {}'.format(compound['properties']['gid'])
    return summary


def delete(source):
    try:
        query = {
          "query": {
            "query_string": {
              "analyze_wildcard": True,
              "query": "source:{}".format(source)
            }
          }
        }
        es.delete_by_query(index='genes', body=query)
    except Exception as e:
        print e, query
        pass


def delete_index():
    # delete index
    try:
        indices_client = IndicesClient(es)
        indices_client.delete(index='genes2')
    except Exception as e:
        print e
        pass

# main
# delete_index()
print json.dumps(harvest())
