#!/usr/bin/python

# sys libs
import datetime
import logging
import yaml
import urllib2
import sys
import re
import argparse
import sys
import os
import socket
import json

# backend
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A

# webserver
import connexion
from flask_cors import CORS
from OpenSSL import SSL

# our utils
from log_setup import init_logging

# ***** globals
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = None
# swagger doc
# beacon_api = None
g2p_api = None
# defaults
ARGS = None
# *****


init_logging()
log = logging.getLogger(__name__)


# controllers *****************************
# API_URL = 'https://app.swaggerhub.com/apiproxy/schema/file/ELIXIR-Finland/ga-4_gh_beacon_api_specification/0.4.0/swagger.yaml'  # noqa

DESCRIPTION = """
The Variant Interpretation for Cancer Consortium (VICC)
The VICC is a Driver Project of the Global Alliance for Genomics Health (GA4GH).
The field of precision medicine aspires to a future in which a cancer patient's molecular information can be used to inform diagnosis, prognosis and treatment options most likely to benefit that individual patient. Many groups have created knowledgebases to annotate cancer genomic mutations associated with evidence of pathogenicity or relevant treatment options. However, clinicians and researchers are unable to fully utilize the accumulated knowledge derived from such efforts. Integration of the available knowledge is currently infeasible because each group (often redundantly) curates their own knowledgebase without adherence to any interoperability standards. Therefore, there is a clear need to standardize and coordinate clinical-genomics curation efforts, and create a public community resource able to query the aggregated information. To this end we have formed the Variant Interpretation for Cancer Consortium (VICC) to bring together the leading institutions that are independently developing comprehensive cancer variant interpretation databases.
"""  # NOQA


VICC_BEACON = {
    "id": "vicc",
    "name": "VICC",
    "url": None,
    "organization": "VICC",
    "description": DESCRIPTION,
    "homePage": "http://cancervariants.org/",
    "email": "vicc_paper@genomicsandhealth.org",
    "aggregator": True,
    "visible": True,
    "enabled": True,
    "supportedReferences": [
      "GRCH37"
    ]
}


def _es():
    """ get an elastic search connection """
    return Elasticsearch(['{}'.format(ARGS.elastic)])


# utilities used by controllers
class Params():
    """ turn parameter dict to a class"""
    def __init__(self, args):
        self.referenceName = args.get('referenceName', None)
        self.start = args.get('start', None)
        self.startMin = args.get('startMin', None)
        self.startMax = args.get('startMax', None)
        self.end = args.get('end', None)
        self.endMin = args.get('endMin', None)
        self.endMax = args.get('endMax', None)
        self.referenceBases = args.get('referenceBases', None)
        self.alternateBases = args.get('alternateBases', None)
        self.assemblyId = args.get('assemblyId', None)
        self.datasetIds = args.get('datasetIds', None)
        self.includeDatasetResponses = args.get('includeDatasetResponses',
                                                None)


def _location_lookup(params):
    """ perform elastic search query """
    client = _es()

    # build parameters for query, and echo query to response
    args = {}
    if params.assemblyId:
        args['features.referenceName'] = params.assemblyId
    if params.referenceName:
        args['features.chromosome'] = params.referenceName
    if params.start:
        args['features.start'] = params.start
    if params.end:
        args['features.end'] = params.end
    if params.referenceBases:
        args['features.ref'] = params.referenceBases
    if params.alternateBases:
        args['features.alt'] = params.alternateBases
    print args

    q = Search(using=client)
    query = ' '.join(['+{}:{}'.format(k, args[k]) for k in args.keys()])
    q = q.query("query_string", query=query)
    count = q.count()
    return {
        "beaconId": VICC_BEACON['id'],
        "apiVersion": g2p_api.specification['info']['version'],
        "exists": count > 0,
        "datasetAlleleResponses": [
            {
                'externalUrl': '{}://{}/v1/g2p/associations/{}'.format(
                    g2p_api.specification['schemes'][0],
                    g2p_api.specification['host'],
                    hit.meta.id),
                'note': hit.association.description,
            }
            for hit in q]
    }


# These are imported by name by connexion so we create them here.
def getBeacon():
    """ static beacon """
    return VICC_BEACON


def getBeaconAlleleResponse(**kwargs):
    """ lookup by allele (aka variant/feature) """
    return _location_lookup(Params(kwargs))


def postBeaconAlleleResponse(queryBeaconAllele):
    """ lookup by allele (aka variant/feature) """
    log.debug(queryBeaconAllele)
    return _location_lookup(Params(queryBeaconAllele))


def searchAssociations(**kwargs):
    """ return matching associations"""
    log.debug(kwargs)
    client = _es()
    q = kwargs.get('q', '*')
    s = Search(using=client, index='associations')
    s = s.query("query_string", query=q)
    # grab total before we apply size
    total = s.count()
    size = int(kwargs.get('size', '10'))
    _from = int(kwargs.get('from', '1'))
    # set sort order
    sort = kwargs.get('sort', None)
    if sort:
        (field, order) = sort.split(':')
        if order == 'desc':
            field = '-{}'.format(field)
        if '.keyword' not in field:
            field = '{}.keyword'.format(field)
        log.debug('set sort to {}'.format(field))
        s = s.sort(field)
    log.debug(s.to_dict())
    return {
        'hits': {
            'total': total,
            'hits': [hit.to_dict() for hit in s[_from:(_from+size)]]
        }
    }


def associationTerms(**kwargs):
    log.debug(kwargs)
    client = _es()
    q = kwargs.get('q', '*')
    field = kwargs.get('f')
    if not field.endswith('.keyword'):
        field = '{}.keyword'.format(field)
    # create a search, ...
    s = Search(using=client, index='associations')
    # with no data ..
    s = s.params(size=0)
    s = s.query("query_string", query=q)
    # ... just aggregations
    s.aggs.bucket('terms', 'terms', field=field)
    print s.to_dict()
    aggs = s.execute().aggregations
    # map it to an array of objects
    return aggs.to_dict()
    # return [{'phenotype_description': b.key,
    #          'phenotype_ontology_id': b.phenotype_id.buckets[0].key,
    #          'phenotype_evidence_count':b.phenotype_id.buckets[0].doc_count} for b in aggs.phenotype_descriptions.buckets]


def getAssociation(**kwargs):
    """ return  a single association"""
    log.debug(kwargs)
    client = _es()
    association = client.get(index="associations",
                             doc_type='association', id=kwargs['id'])
    return association['_source']


# setup server

def configure_app(args):
    """ configure the app, import swagger """
    global application
#    global beacon_api
    global g2p_api

    def function_resolver(operation_id):
        """Map the operation_id to the function in this class."""
        if '.' in operation_id:
            _, function_name = operation_id.rsplit('.', 1)
        else:
            function_name = operation_id
        function = getattr(sys.modules[__name__], function_name)
        return function

    app = connexion.App(
        __name__,
        swagger_ui=True,
        swagger_json=True)
    CORS(app.app)

    swagger_host = None
    if args.swagger_host:
        swagger_host = args.swagger_host
    else:
        host = 'localhost'  # socket.gethostname()
        if args.port != 80:
            host += ':{}'.format(args.port)
        swagger_host = '{}'.format(host)

    # with open('swagger-beacon.yaml', 'r') as stream:
    #     swagger_beacon = yaml.load(stream)
    #
    # with open('swagger-g2p.yaml', 'r') as stream:
    #     swagger_combined = yaml.load(stream)
    #
    # swagger_beacon['host'] = swagger_host
    # swagger_combined['host'] = swagger_host

    with open('swagger-combined.yaml', 'r') as stream:
        swagger_combined = yaml.load(stream)

    swagger_combined['host'] = swagger_host

    log.info('advertise swagger host as {}'.format(swagger_host))

    # # remove schemes that do not apply
    # if args.key_file:
    #     # swagger_beacon['schemes'].remove('http')
    #     swagger_combined['schemes'].remove('http')
    # else:
    #     # swagger_beacon['schemes'].remove('https')
    #     swagger_combined['schemes'].remove('https')

    # beacon_api = app.add_api(swagger_beacon, base_path='/v1/beacon',
    #                          resolver=function_resolver)

    g2p_api = app.add_api(swagger_combined, base_path='/api/v1',
                          resolver=function_resolver)

    log.info('g2p_api.version {}'.format(
             g2p_api.specification['info']['version']
             ))
    # set global
    application = app.app
    return (app, g2p_api)


def run(args):
    """ configure and start the apps """
    (app, g2p_api) = configure_app(args)
    if args.key_file:
        context = (args.certificate_file, args.key_file)
        app.run(port=args.port, ssl_context=context, host='0.0.0.0')
    else:
        app.run(port=args.port, host='0.0.0.0')


def setup_args():
    # run our standalone flask server
    argparser = argparse.ArgumentParser(
        description='GA4GH Beacon & G2P webserver')
    argparser.add_argument('-P', '--port', default=8080, type=int)
    argparser.add_argument('-K', '--key_file', default=None)
    argparser.add_argument('-C', '--certificate_file', default=None)
    es_host = os.getenv('ES', 'http://localhost')
    argparser.add_argument('-ES', '--elastic', default=es_host)
    argparser.add_argument('-H', '--swagger_host', default=None,
                           help='Swagger hostname, defaults to localhost')
    return argparser.parse_args()


def test():
    """ setup test config"""
    global ARGS

    class TestArgs:
        def __init__(self):
            self.port = 8080
            self.key_file = None
            self.elastic = os.getenv('ES', 'http://localhost')
            self.swagger_host = None
    ARGS = TestArgs()
    log.info(ARGS)
    configure_app(ARGS)


def main():
    global ARGS
    ARGS = setup_args()
    log.info(ARGS)
    run(ARGS)


if __name__ == '__main__':
    main()
