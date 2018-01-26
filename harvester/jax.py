
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from inflection import parameterize, underscore
import json
import re

import logging
import evidence_label as el
import evidence_direction as ed

import cosmic_lookup_table
from attrdict import AttrDict
import time

LOOKUP_TABLE = None
gene_list = None

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# see https://ckb.jax.org/about/curationMethodology


def _parse_profile(profile):
    parts = profile.split()
    global LOOKUP_TABLE
    global gene_list
    if not LOOKUP_TABLE:
        logging.info('_parse_profile: init LOOKUP_TABLE')
        LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                "./cosmic_lookup_table.tsv")
    parts = profile.split()
    # this list taken from https://ckb.jax.org/about/glossaryOfTerms
    # "Non specific variants" list, separated by space, where applicable
    jax_biomarker_types = [
        'act',
        'amp',
        'dec',
        'del',
        'exp',
        'fusion',
        'inact',
        'loss',
        'mut',
        'mutant',
        'negative',
        'over',
        'pos',
        'positive',
        'rearrange',
        'wild-type'
    ]
    if not gene_list:
        gene_list = LOOKUP_TABLE.get_genes()
    genes = []
    muts = []
    biomarkers = []
    biomarker_types = None
    fusions = []
    # Complex loop: Run through the split profile, creating four arrays,
    # one of the indices of genes in `parts`, one of the indices of mutations
    # in `parts` (if present, `None` if not), one of biomarker strings,
    # (if present, `None` if not), and a fusions array. Gene, mutation, and
    # biomarker arrays should always have same length.
    for i in range(len(parts)):
        # check for fusions
        if '-' in parts[i] and parts[i] not in jax_biomarker_types:
            fusion = parts[i].split('-')
            if fusion[0] in gene_list and fusion[1] in gene_list:
                fusions.append(parts[i].split('-'))
                # if you're dealing with a fusion with no other gene listed,
                # use the fusion as the gene
                if i+1 == len(parts):
                    pass
                elif len(parts) > 1 and parts[i+1] not in gene_list:
                    genes.append(parts[i])
                    biomarker_types = []
                continue
       # check to see if you're on a gene
        if parts[i] in gene_list:
            genes.append(parts[i])
            # reset the biomarker_type array on every new gene
            biomarker_types = []
            continue
        # check to see if part matches a mutation variant format, e.g. `V600E`
        if re.match("[A-Z][0-9]+[fs]?[*]?[0-9]?[A-Z]?", parts[i]):
            muts.append(parts[i])
            if i+1 == len(parts) or parts[i+1].split('-')[0] in gene_list:
                biomarkers.append([''])
            continue
        # Should only hit this if there's no mutation listed for the present gene,
        # so denote that and catch the biomarker.
        elif len(genes) != len(muts):
            muts.append('')
        if parts[i] in jax_biomarker_types:
            biomarker_types.append(parts[i])
            if i+1 == len(parts) or parts[i+1].split('-')[0] in gene_list:
                biomarkers.append(biomarker_types)
        elif len(genes) != len(biomarkers):
            biomarkers.append([''])
    # change the internal biomarker_type arrays into strings
    biomarker_types = []
    for biomarker in biomarkers:
        if biomarker[0]:
            biomarker_types.append(' '.join(biomarker))
        else:
            biomarker_types.append('')
    return genes, muts, biomarker_types, fusions


def harvest(genes):
    """ get data from jax, ignore genes - get all """
    for gene in _get_gene_ids():
        for jax_evidence in get_evidence([gene]):
            yield jax_evidence


def _get_gene_ids():
    """ call api, get genes """
    offset = 0
    size = 100
    gene_count = 0
    while offset > -1:
        url = 'https://ckb.jax.org/ckb-api/api/v1/genes?offset={}&max={}' \
                .format(offset, size)
        response = AttrDict(
            requests.get(url, verify=False, timeout=120).json())
        gene_count = gene_count + len(response.genes)
        if gene_count >= response.totalCount:
            offset = -1
        else:
            offset = offset + size
        for gene in response.genes:
            yield gene


def get_evidence(genes):
    # [
    #   {
    #     "id": 11048,
    #     "approvalStatus": "Clinical Study",
    #     "evidenceType": "Actionable",
    for gene in genes:
        url = 'https://ckb.jax.org/ckb-api/api/v1/genes/{}/evidence' \
                .format(gene.id)
        response = requests.get(url, verify=False, timeout=120).json()
        for evidence in response:
            yield AttrDict({'gene': gene.geneSymbol,
                            'jax_id': gene.id,
                            'evidence': evidence})


def convert(jax_evidence):
    global LOOKUP_TABLE
    gene = jax_evidence.gene
    jax = jax_evidence.jax_id
    evidence = jax_evidence.evidence
    # TODO: alterations are treated individually right now, but they are
    # actually combinations and should be treated accordingly.

    # Parse molecular profile and use for variant-level information.
    profile = evidence.molecularProfile.profileName.replace('Tp53', 'TP53').replace(' - ', '-')
    gene_index, mut_index, biomarkers, fusions = _parse_profile(profile)

    if not (len(gene_index) == len(mut_index) == len(biomarkers)):
        logging.warning(
            "ERROR: This molecular profile has been parsed incorrectly!")
        logging.warning(json.dumps(
            {"molecular_profile": evidence.molecularProfile},
            indent=2, sort_keys=True))
        return

    features = []
    parts = profile.split()

    startTime = time.time()
    for i in range(len(gene_index)):
        feature = {}
        feature['geneSymbol'] = gene_index[i]
        feature['name'] = ' '.join([gene_index[i],
                                    mut_index[i], biomarkers[i]])
        if biomarkers[i]:
            feature['biomarker_type'] = biomarkers[i]

        # Look up variant and add position information.
        if not LOOKUP_TABLE:
            logging.info("convert:init LOOKUP_TABLE")
            LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                           "./cosmic_lookup_table.tsv")
        startTime2 = time.time()
        matches = LOOKUP_TABLE.get_entries(gene_index[i], mut_index[i])
        logging.info("Time taken LOOKUP_TABLE {} {} {}".format(gene_index[i], mut_index[i], time.time() - startTime2))
        if len(matches) > 0:
            # FIXME: just using the first match for now;
            # it's not clear what to do if there are multiple matches.
            match = matches[0]
            feature['chromosome'] = str(match['chrom'])
            feature['start'] = match['start']
            feature['end'] = match['end']
            feature['ref'] = match['ref']
            feature['alt'] = match['alt']
            feature['referenceName'] = str(match['build'])
        features.append(feature)
    logging.info("Time taken len(gene_index) {}".format(time.time() - startTime))

    for fusion in fusions:
        for gene in fusion:
            feature = {}
            feature['geneSymbol'] = gene
            feature['name'] = '-'.join(fusion)
            feature['biomarker_type'] = 'fusion'
            features.append(feature)

    association = {}
    association['variant_name'] = mut_index
    association['source_link'] = \
        'https://ckb.jax.org/molecularProfile/show/{}' \
        .format(evidence.molecularProfile.id)

    association['description'] = evidence.efficacyEvidence
    association['environmentalContexts'] = []
    association['environmentalContexts'].append({
        'description': evidence.therapy.therapyName})
    i = evidence.indication
    association['phenotype'] = {
        'description': i.name,
        'type': {'term': '{}:{}'.format(i.source, i.id)}
    }
    association['evidence'] = [{
        "evidenceType": {
            "sourceName": "jax"
        },
        'description': evidence.responseType,
        'info': {
            'publications':
                [r.url for r in evidence.references]  # NOQA
        }
    }]
    # add summary fields for Display
    association = el.evidence_label(evidence.approvalStatus, association)
    association = ed.evidence_direction(evidence.responseType, association)

    if len(evidence.references) > 0:
        association['publication_url'] = evidence.references[0].url

    association['drug_labels'] = evidence.therapy.therapyName
    feature_association = {'genes': list(set(gene_index)),
                           'feature_names':
                           evidence.molecularProfile.profileName,
                           'features': features,
                           'association': association,
                           'source': 'jax',
                           'jax': evidence}
    yield feature_association


def harvest_and_convert(genes):
    """ get data from jax, convert it to ga4gh and return via yield """
    startTime = time.time()
    for jax_evidence in harvest(genes):
        # print "Time taken {}".format(time.time() - startTime)
        # print "harvester_yield {}".format(jax_evidence.keys())
        startTime = time.time()
        for feature_association in convert(jax_evidence):
            yield feature_association


def _test():
    for feature_association in harvest_and_convert(None):
        print feature_association
        break

if __name__ == '__main__':
    _test()
