from __future__ import print_function
import sys

import requests
from inflection import parameterize, underscore
import json


def harvest(genes=None):
    with open("pmkb.json", "r") as ins:
        for line in ins:
            yield json.loads(line)


def convert(interpretation):
    yield interpretation


def harvest_and_convert(genes):
    """ get data from pmkb, convert it to ga4gh and return via yield """
    for evidence in harvest(genes):
        # print "harvester_yield {}".format(evidence.keys())
        for feature_association in convert(evidence):
            # print "pmkb convert_yield {}".format(feature_association.keys())
            yield feature_association
