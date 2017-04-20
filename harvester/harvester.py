#!/usr/bin/python
import sys
import argparse
sys.path.append('silos')  # NOQA

import json
import argparse

import jax
import civic
import oncokb
import cgi_biomarkers
import molecularmatch
from elastic_silo import ElasticSilo
import elastic_silo
from kafka_silo import KafkaSilo
import kafka_silo

argparser = argparse.ArgumentParser()

argparser.add_argument('--harvesters',  nargs='+',
                       help='''harvest from these sources. default:
                               [cgi_biomarkers,jax,civic,oncokb,
                               molecularmatch]''',
                       default=['cgi_biomarkers', 'jax', 'civic',
                                'oncokb', 'molecularmatch'])


argparser.add_argument('--silos',  nargs='+',
                       help='''save to these silos. default:[elastic,kafka]''',
                       default=['elastic', 'kafka'])


argparser.add_argument('--delete_index', '-d',
                       help='''delete all from index''',
                       default=False, action="store_true")

argparser.add_argument('--delete_source', '-ds',
                       help='delete all content for any harvester',
                       default=False, action="store_true")


elastic_silo.populate_args(argparser)
kafka_silo.populate_args(argparser)

args = argparser.parse_args()
for h in args.harvesters:
    assert h in sys.modules, "harvester is not a module: %r" % h
print "harvesters: %r" % args.harvesters
print "silos: %r" % args.silos
print "elastic_search: %r" % args.elastic_search
print "elastic_index: %r" % args.elastic_index
print "delete_index: %r" % args.delete_index


def _make_silos(args):
    """ construct silos """
    silos = []
    for s in args.silos:
        if s == 'elastic':
            silos.append(ElasticSilo(args))
        if s == 'kafka':
            silos.append(KafkaSilo(args))
    return silos


silos = _make_silos(args)


# cgi, jax, civic, oncokb
def harvest(genes):
    """ get evidence from all sources """
    for h in args.harvesters:
        harvester = sys.modules[h]
        if args.delete_source:
            for silo in silos:
                silo.delete_source(h)

        for feature_association in harvester.harvest_and_convert(genes):
            yield feature_association


def get_genes(paths=['network-GeneTrails.json']):  # , 'network-cfDNA.json'
    """simple list of gene names"""
    genes = []
    for path in paths:
        network = []
        with open(path) as json_data:
            network = json.load(json_data)
            json_data.close()

        pathway_property_names = ['upstream', 'downstream', 'complex-partner']
        for pathway in network:
            # ensure is array
            genes.append(pathway['gene-symbol'])
            # for pn in pathway_property_names:
            #     if pn in pathway:
            #         genes.extend(pathway[pn])
    return list(set(genes))


def main():
    if args.delete_index:
        for silo in silos:
            silo.delete_all()
    genes = get_genes()
    for feature_association in harvest(genes):
        for silo in silos:
            silo.save(feature_association)

if __name__ == '__main__':
    main()
