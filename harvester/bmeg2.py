import json
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas
import imp
import requests
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
import json
ophion = imp.load_source('ophion_client', 'ophion/client/python/ophion.py')

O = ophion.Ophion("http://bmeg.compbio.ohsu.edu")

es = Elasticsearch(
    ['10.96.11.130']
)


def exec_ophion(query):
    """ given a query check it for errors, if found raise it
        , otherwise return results """
    ophion_result = query.execute()
    if 'error' in ophion_result:
        raise ophion_result['error']
    else:
        return ophion_result["result"]

#  get the list of drugs
print 'getting drugs'
drugs = list(set(exec_ophion(O.query().has("gid", "cohort:CCLE")
                                      .outgoing("hasMember")
                                      .incoming("responseOf")
                                      .outgoing("responseTo")
                                      .values(["gid"]))))

print 'got {} drugs'.format(len(drugs))

# this is a list of [gid,histology,gid,histology,gid,histology,...]
print 'getting diseases'
diseases = list(set(exec_ophion(O.query().has("gid", "cohort:CCLE")
                                         .outgoing("hasMember").mark("a")
                                         .outgoing("diseaseOf").mark("b")
                                         .select("b").values(["gid"]))))
print 'got {} diseases'.format(len(diseases))

all_samples_hash = {}
for disease in diseases:
    print 'getting samples for disease {}'.format(disease)
    samples = exec_ophion(O.query().has("gid", disease)
                                   .incoming("diseaseOf")
                                   .values(["gid"]))
    # print 'got {} samples for disease {}'.format(len(samples), disease)
    all_samples_hash[disease] = {'samples': samples}


print 'all_samples_hash:'
for disease in all_samples_hash.keys():
    print '  ', disease, len(all_samples_hash[disease]['samples'])


# now do the same for mutation
genes = ['CCND1', 'CDKN2A', 'CHEK1', 'DDR2', 'FGF19', 'FGF3', 'FGF4', 'FGFR1', 'IDO1', 'IDO2', 'MDM4', 'RAD51D']
for gene in genes:
    print 'getting mut_samples {}'.format(gene)
    for disease in diseases:
        print 'getting mut samples for disease {}'.format(disease)
        samples = exec_ophion(O.query().has("gid", disease)
                                       .incoming("diseaseOf").mark('a')
                                       .incoming("callsFor")
                                       .incoming("inCallSet")
                                       .incoming("annotationFor")
                                       .outgoing("transcriptEffectOf")
                                       .outgoing("affectsGene")
                                       .has("gid", "gene:%s" % (gene))
                                       .select('a')
                                       .values(["gid"])
                              )
        print 'got {} samples for disease {}'.format(len(samples), disease)
        if 'gene_mutations' not in all_samples_hash[disease]:
            all_samples_hash[disease]['gene_mutations'] = {}
        all_samples_hash[disease]['gene_mutations'][gene] = {'samples': samples}

print 'all_samples_hash:'
for disease in all_samples_hash.keys():
    print '  ', disease
    print '     ALL', len(all_samples_hash[disease]['samples'])
    for gene in all_samples_hash[disease]['gene_mutations'].keys():
        print '    {}'.format(gene), len(all_samples_hash[disease]['gene_mutations'][gene]['samples'])

# now get the AUC for all histologies, comparing diff b/t mutation & normal

# callback we use below
def get_set_drug_summaries(samples, drug, responseType):
    data = O.query().has("gid", drug).incoming("responseTo").mark("a").outgoing("responseOf").has("gid", samples).select("a").values(["gid", "responseSummary"]).execute()['result']
    data_map = dict(list( (data[i], json.loads(data[i+1])) for i in range(0, len(data), 2) ))
    values = list( filter(lambda x:x["type"] == responseType, i) for i in data_map.values())
    values = filter(lambda x: len(x) > 0, values)
    values = map(lambda x:x[0]['value'], values)
    return values


for disease in all_samples_hash.keys():
    all_samples = all_samples_hash[disease]['samples']
    for gene in all_samples_hash[disease]['gene_mutations'].keys():
        mut_samples = all_samples_hash[disease]['gene_mutations'][gene]['samples']
        if len(mut_samples) > 2:
            print 'getting AUC for {} {}'.format(disease, gene)
            norm_samples = list(set(all_samples).difference(mut_samples))
            out = []
            for drug in drugs:
                print 'pvalues for {} {} {} {} {}'.format(disease, gene, drug, len(all_samples), len(mut_samples))
                mut_values = get_set_drug_summaries(mut_samples, drug, "AUC")
                norm_values = get_set_drug_summaries(norm_samples, drug, "AUC")
                s = stats.ttest_ind(mut_values, norm_values, equal_var=False)
                print '   ', s
                if s.pvalue > 0:
                    out.append( {"drug" : drug, "statistic" : s.statistic, "pvalue" : s.pvalue} )
                    # now restructure mut_samples[histology] to { samples:[gid,...], pvalues:[{drug,pvalue,statistic}]}
                    #mut_samples_histologies[histology] = {'samples': mut_samples, 'pvalues': out }
                    body = {'gene': gene, 'disease':disease, "drug" : drug, 'samples': mut_samples , "statistic": s.statistic, "pvalue": s.pvalue}
                    # result = es.index(index='bmeg', body=body, doc_type='bmeg',  op_type='index')
                    # if result['_shards']['failed'] > 0:
                    #     print 'failure updating gene {} histology {}'.format(gene, disease)
                    # else:
                    #     print 'OK updating gene gene {} histology {}'.format(gene, disease)
