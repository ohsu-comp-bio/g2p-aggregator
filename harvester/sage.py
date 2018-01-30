import synapseclient
import evidence_label as el
import evidence_direction as ed


def _synData():
    synapseid = 'syn7155100'
    # print("made it in synData")
    syn = synapseclient.login(silent=True)
    result = syn.tableQuery('select * from %s' % synapseid)
    df = result.asDataFrame()
    yield df


def _getValues(key, listDict):
    return [val[key] for val in listDict if key in val]


def harvest(genes):
    # print("made it in harvest")
    df = list(_synData())[0]
    gene_evidences = []
    # harvest all genes
    if not genes:
        # convert gene dataframe to a list of dictionary objects per row
        gene_evidences = df.to_dict(orient='records')
        for gene_evidence in gene_evidences:
            gene_data = {gene_evidence['gene']: [gene_evidence]}
            yield [gene_data]
    else:
        for gene in genes:
            gene_evidences = df.loc[df.gene == gene].to_dict(orient='records')
            for gene_evidence in gene_evidences:
                gene_data = {gene_evidence['gene']: [gene_evidence]}
                yield [gene_data]


def convert(gene_data):
    # print "made it in convert", list(gene_data)[0]
    gene_list = list(gene_data)[0]
    gene, evidence = gene_list.popitem()
    for index, evidence_item in enumerate(evidence):
        feature = {
                    "geneSymbol": gene,
                    'entrez_id': evidence_item['entrez_id'],
                    'info': {
                        'germline_or_somatic':
                        evidence_item['germline_or_somatic']
                    }
                  }

        for index, evidence_item in enumerate(evidence):
            description = '{} {} {}'.format(
                evidence_item['clinical_manifestation'],
                evidence_item['response_type'],
                evidence_item['drug_labels']
            )
            association = {
                'description': description,
                'phenotype': {
                    'description': evidence_item['clinical_manifestation'],
                },
                'evidence': [{
                    "evidenceType": {
                        "sourceName": "sage",
                        "id": '{}'.format(evidence_item['publication_url'])
                    },
                    'description': description,
                    'info': {
                        'publications': [evidence_item['publication_url']]
                    }
                }]
            }
            association['environmentalContexts'] = [{
                'description': evidence_item['drug_labels'],
            }]

            association = el.evidence_label(evidence_item['evidence_label'],
                                            association, na=False)
            association = ed.evidence_direction(evidence_item['response_type'],
                                                association)

            feature_association = {'genes': [gene],
                                   'features': [feature],
                                   'association': association,
                                   'source': 'sage',
                                   'sage': evidence_item}
            yield feature_association


def harvest_and_convert(genes):
    """ get data from civic, convert it to ga4gh and return via yield """
    for gene_data in harvest(genes):
        #print "harvester_yield {}".format(gene_data)
        for feature_association in convert(gene_data):
            # print "convert_yield {}".format(feature_association.keys())
            yield feature_association


if __name__ == '__main__':
    for feature_association in harvest_and_convert(['NF2']):
        print feature_association
        break
