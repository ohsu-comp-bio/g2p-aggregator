#!/usr/bin/python
# -*- coding: utf-8 -*-
import genes
import local
import logging

# biostream-schema
from bmeg.clinical_pb2 import *
from bmeg.cna_pb2 import *
from bmeg.genome_pb2 import *
from bmeg.phenotype_pb2 import *
from bmeg.rna_pb2 import *
from bmeg.variants_pb2 import *
from google.protobuf import json_format
import json
from google.protobuf.json_format import MessageToJson

# standardized ID generation
from vmc import models, computed_id, vmc_serialize, get_vmc_sequence_id


logger = logging.getLogger(__name__)

# keep track of what we've already exported
exported = []


def get_accession(chromosome):
    ''' return accession for chromosome
        https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh37.p13
        https://www.ncbi.nlm.nih.gov/nuccore/NC_000019.09
    '''
    ac_map = {
        '1': 'NC_000001.10',
        '2': 'NC_000002.11',
        '3': 'NC_000003.11',
        '4': 'NC_000004.11',
        '5': 'NC_000005.9',
        '6': 'NC_000006.11',
        '7': 'NC_000007.13',
        '8': 'NC_000008.10',
        '9': 'NC_000009.11',
        '10': 'NC_000010.10',
        '11': 'NC_000011.9',
        '12': 'NC_000012.11',
        '13': 'NC_000013.10',
        '14': 'NC_000014.8',
        '15': 'NC_000015.9',
        '16': 'NC_000016.9',
        '17': 'NC_000017.10',
        '18': 'NC_000018.9',
        '19': 'NC_000019.9',
        '20': 'NC_000020.10',
        '21': 'NC_000021.8',
        '22': 'NC_000022.10',
        'X': 'NC_000023.10',
        '23': 'NC_000023.10',
        'Y': 'NC_000024.9',
    }
    return ac_map.get(chromosome, None)


def get_GRCh37_identifier():
    return models.Identifier(namespace="NCBI",
                             accession="NC_000019.9")


def vmc_identifier(chromosome):
    ''' return VMC identifier for chromosome '''
    identifier = models.Identifier(namespace="NCBI",
                                   accession=get_accession(chromosome))
    return identifier


def vmc_location(feature):
    """
    given a feature, create a VMC identifier
    https://github.com/ga4gh/vmc-python
    """
    identifier = vmc_identifier(feature['chromosome'])
    start = None
    end = None
    if 'start' in feature:
        start = int(feature['start'])
    if 'end' in feature:
        end = int(feature['end'])

    interval = models.Interval(start=start, end=end)

    location = models.Location(sequence_id=get_vmc_sequence_id(identifier),
                               interval=interval)
    location.id = computed_id(location)

    return location, identifier


def vmc_allele(feature):
    """
    given a feature, create a VMC identifier
    https://github.com/ga4gh/vmc-python
    """
    location, identifier = vmc_location(feature)

    alt = feature.get('alt', None)
    if alt == '-':
        alt = None
    allele = None
    ref = feature.get('ref', None)
    if ref == '-':
        ref = None

    if alt:
        allele = models.Allele(location_id=location.id, state=a)
    elif ref:
        allele = models.Allele(location_id=location.id, state=ref)
    if allele:
        allele.id = computed_id(allele)

    return allele, location, identifier


def vmc_bundle(feature):

    location = vmc_location(feature)
    allele, location, identifier = vmc_allele(feature)
    locations = {location.id: location}
    identifiers = {location.sequence_id: [identifier]}
    alleles = {allele.id: allele}

    return models.Vmcbundle(locations=locations, alleles=alleles,
                            identifiers=identifiers)


def feature_gid(f):
    """ given a feature, hash it"""
    a = []
    empty_count = 0
    gid_name = ''  # no 'variant:' as start
    for p in ['referenceName', 'chromosome', 'start',
              'end', 'ref', 'alt']:
        a.append(str(f.get(p, '')))
    if 'start' not in f:
        a = []
        geneSymbol = f.get('geneSymbol', None)
        if geneSymbol:
            gene_name = genes.gene_lookup(geneSymbol)
            if gene_name:
                a.append(gene_name.id)
            else:
                logger.warn('no ensembl for {}'.format(geneSymbol))
        description = f.get('description', None)
        if not description:
            gid_name = 'gene'
        else:
            a.append(description)
    return gid_name + ':'.join(a)


def _variant(feature, gid):
    v = {
        'id': gid,
    }
    v['names'] = []
    if 'synonyms' in feature:
        v['names'].extend(feature['synonyms'])
    if 'links' in feature:
        v['names'].extend(feature['links'])
    if 'name' in feature:
        v['names'].append(feature['name'])
    if 'entrez_id' in feature:
        v['names'].append(str(feature['entrez_id']))
    if 'biomarker_type' in feature:
        v['variant_type'] = feature['biomarker_type']
    if 'start' in feature:
        v['start'] = feature['start']
    if 'end' in feature:
        v['end'] = feature['end']
    if 'chromosome' in feature:
        v['reference_name'] = feature['chromosome']
    if 'referenceName' in feature:
        v['reference_genome'] = feature['referenceName']
    if 'ref' in feature:
        v['reference_bases'] = feature['ref']
    if 'alt' in feature and feature['alt']:
        v['alternate_bases'] = [feature['alt']]

    return v


def normalize(hit):
    """ returns a tuple of (hit, features), where hit has been modified to
    normalize hit.features[] and the  features[] array
    contains features observed in this hit that have not yet been returned
    """
    features = {}
    remove_from_hit = []
    already_exported = []
    # hash each feature
    for feature in hit['features']:
        gid = feature_gid(feature)
        features[gid] = _variant(feature, gid)
    hit['features'] = list(features.keys())
    for k in features.keys():
        if k in exported:
            del features[k]
    exported.extend(features.keys())
    return (hit, features)


if __name__ == '__main__':
    """ testing """
    COMPLEX_FEATURE = \
        {
          "end": 55593615,
          "description": "KIT V559_E561del",
          "start": 55593607,
          "biomarker_type": "nonsense",
          "referenceName": "GRCh37",
          "alt": "-",
          "ref": "AGGTTGTTG",
          "chromosome": "4",
          "name": "KIT V559_E561del"
        }
    ttl = normalize({'features': [
        {
            "geneSymbol": "TTL"
        }
    ]})
    assert (({'features': ['geneENSG00000114999']}, {'geneENSG00000114999': {'id': 'geneENSG00000114999', 'names': []}})) == ttl    # noqa
    complex_rsp = normalize({'features': [
        COMPLEX_FEATURE,
    ]})
    # print complex_rsp
    assert ({'features': ['GRCh37:4:55593607:55593615:AGGTTGTTG:-']}, {'GRCh37:4:55593607:55593615:AGGTTGTTG:-': {'end': 55593615, 'reference_genome': 'GRCh37', 'reference_name': '4', 'alternate_bases': ['-'], 'reference_bases': 'AGGTTGTTG', 'start': 55593607, 'variant_type': 'nonsense', 'names': ['KIT V559_E561del'], 'id': 'GRCh37:4:55593607:55593615:AGGTTGTTG:-'}}) == complex_rsp  # noqa

    complex_ttl = normalize({'features': [
        {
            "geneSymbol": "TTL"
        },
        COMPLEX_FEATURE
    ]})
    assert ({'features': ['geneENSG00000114999', 'GRCh37:4:55593607:55593615:AGGTTGTTG:-']}, {}) == complex_ttl, 'should be \n{}'.format(complex_ttl)   # noqa

    v = Variant()
    o = json_format.Parse(json.dumps(complex_rsp[1]['GRCh37:4:55593607:55593615:AGGTTGTTG:-']), v, ignore_unknown_fields=False)
    assert(MessageToJson(o))

    location = vmc_location(COMPLEX_FEATURE)
    print location
    allele = vmc_allele(COMPLEX_FEATURE)
    print allele
    bundle = vmc_bundle(COMPLEX_FEATURE)
    print bundle.as_dict()
    print bundle.keys()
