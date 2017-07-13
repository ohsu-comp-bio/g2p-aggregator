#!/usr/bin/python

from ga4gh.client import client
import json
import ga4gh.client.protocol as protocol

ga4gh_endpoint = "http://10.96.11.130:8000"
c = client.HttpClient(ga4gh_endpoint)

def harvest(genes):
    datasets = c.search_datasets()
    phenotype_association_set_id = None
    phenotype_association_set_name = None
    for  dataset in datasets:
      phenotype_association_sets = c.search_phenotype_association_sets(dataset_id=dataset.id)
      for phenotype_association_set in phenotype_association_sets:
        phenotype_association_set_id = phenotype_association_set.id
        phenotype_association_set_name = phenotype_association_set.name
        # print 'Found G2P phenotype_association_set:', phenotype_association_set.id, phenotype_association_set.name
        break

    assert phenotype_association_set_id
    assert phenotype_association_set_name

    feature_set_id = None
    datasets = c.search_datasets()
    for  dataset in datasets:
      featuresets = c.search_feature_sets(dataset_id=dataset.id)
      for featureset in featuresets:
        if phenotype_association_set_name in featureset.name:
          feature_set_id = featureset.id
          # print 'Found G2P feature_set:', feature_set_id
          break
    assert feature_set_id

    gene_features = []
    for gene in set(genes):
        feature_generator = c.search_features(feature_set_id=feature_set_id, name='.*{}.*'.format(gene))
        features = list(feature_generator)
        if len(features) == 0:
            # print "{} Found no features".format(gene)
            gene_features.append({'gene': gene})
        else:
            # print "{} Found {} features in G2P feature_set {}".format(gene, len(features),feature_set_id)
            a = []
            for f in features:
                a.append(json.loads(protocol.toJson(f)))
            gene_features.append({'gene': gene, 'features': a})


    for gene_feature in gene_features:
        if 'features' in gene_feature:
            for f in gene_feature['features']:
                feature_phenotype_associations =  c.search_genotype_phenotype(
                                                    phenotype_association_set_id=phenotype_association_set_id,
                                                    feature_ids=[f['id']])
                associations = list(feature_phenotype_associations)
                a = []
                for association in associations:
                    a.append(json.loads(protocol.toJson(association)))
                f['associations'] = a
                # print "{} has {} associations".format(gene_feature['gene'], len(a))


    for gene_feature in gene_features:
        gene_feature['ga4gh'] = {}
        if 'features' in gene_feature:
            gene_feature['ga4gh']['features'] = gene_feature['features']
            del gene_feature['features']
        yield gene_feature


def convert(gene_feature):
    gene = gene_feature['gene']
    ga4gh = gene_feature['ga4gh']
    if 'features' in ga4gh:
        for f in ga4gh['features']:
            associations = f['associations']
            del f['associations']
            for a in associations:
                # add summary fields for Display
                a['evidence_label'] = a['evidence'][0]['description']
                url = None
                for e in a['evidence']:
                    for p in e['info']['publications']:
                        url = p
                        break
                drugs = []
                for e in a['environmentalContexts']:
                    drugs.append(e['description'])
                a['publication_url'] = p
                a['drug_labels'] = ','.join(drugs)

                feature_association = {'gene': gene,
                                       'feature': f,
                                       'association': a,
                                       'source':'ga4gh'}
                yield feature_association


def harvest_and_convert(genes):
    """ get data from oncokb, convert it to ga4gh and return via yield """
    for gene_feature in harvest(genes):
        # print "g2p harvester_yield {}".format(gene_feature.keys())
        for feature_association in convert(gene_feature):
            # print "g2p convert_yield {}".format(feature_association.keys())
            yield feature_association


def main():
    for feature_association in harvest_and_convert(['FGFR1']):
        print feature_association.keys()

if __name__ == '__main__':
    main()
