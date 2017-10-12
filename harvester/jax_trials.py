
import sys
from lxml import html
from lxml import etree
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from inflection import parameterize, underscore
import json
import logging
import evidence_label as el
import evidence_direction as ed
import mutation_type as mut

import cosmic_lookup_table

LOOKUP_TABLE = None

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# see https://ckb.jax.org/about/curationMethodology


def harvest(genes):
    """ get data from jax """
    for trial_info in _get_trials_ids():
        for jax_evidence in get_evidence([trial_info]):
            yield jax_evidence


def _get_trials_ids():
    """gets json for list of all trials yield"""
    offset = 0
    while True:
        url = 'https://ckb.jax.org/ckb-api/api/v1/clinicalTrials?offset={}&max=100'.format(offset)
        page = requests.get(url, verify=False)
        trials_ids = []
        trials_infos = page.json()['clinicalTrials']
        if len(trials_infos) == 0:
            break
        offset = offset + 100
        for trial_info in trials_infos:
            yield {'id': trial_info['nctId'], 'trial': trial_info}


def get_evidence(trial_infos):
    """ scrape webpage """
    gene_evidence = []
    for trial_info in trial_infos:
        url = 'https://ckb.jax.org/ckb-api/api/v1/clinicalTrials/{}'.format(trial_info['id'])
        page = requests.get(url, verify=False)
        clinicalTrial = page.json()
        if clinicalTrial['variantRequirements'] == 'no' or len(clinicalTrial['variantRequirementDetails']) == 0:
            logging.info('no variants, skipping {}'.format(trial_info['id']))
            break
        yield {'jax_id': trial_info['id'], 'evidence': clinicalTrial}  # NOQA


def convert(jax_evidence):
    jax = jax_evidence['jax_id']
    evidence = jax_evidence['evidence']
    genes = set([])
    profiles = []
    for detail in evidence['variantRequirementDetails']:
        profileName = detail['molecularProfile']['profileName']
        genes.add(profileName.split(' ')[0])
        profiles.append(profileName)
    genes = list(genes)

    features = []
    for profile in profiles:
        # Parse molecular profile and use for variant-level information.
        genes_from_profile, tuples = _parse(profile)
        for tuple in tuples:
            feature = {}
            feature['geneSymbol'] = tuple[0]
            feature['name'] = tuple[0]
            # feature['name'] = ' '.join(tuple[1:])
            feature['biomarker_type'] = mut.norm_biomarker(' '.join(tuple[1:]))
            try:
                """
                 filter out
                 "FLT3 D835X FLT3 exon 14 ins"
                """
                exceptions = set(["exon", "ins", "amp", "del", "exp", "dec"])
                profile = set(tuple)
                if len(exceptions.intersection(profile)) > 0:
                    print 'skipping ', evidence['molecular_profile']
                    matches = []
                else:
                    # Look up variant and add position information.
                    if not LOOKUP_TABLE:
                        LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                                        "./cosmic_lookup_table.tsv")
                    matches = LOOKUP_TABLE.get_entries(tuple[0],
                                                       ' '.join(tuple[1:]))
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
            except:
                pass
            features.append(feature)

    association = {}
    association['description'] = evidence['title']
    association['environmentalContexts'] = []
    for therapy in evidence['therapies']:
        association['environmentalContexts'].append({
            'description': therapy['therapyName']})
    for indication in evidence['indications']:
        association['phenotype'] = {
            'description': indication['name']
        }
    association['evidence'] = [{
        "evidenceType": {
            "sourceName": "jax-trials"
        },
        'description': evidence['title'],
        'info': {
            'publications':
                'https://clinicaltrials.gov/ct2/show/{}'.format(jax)
        }
    }]
    # add summary fields for Display
    association['evidence_label'] = 'D'
    feature_association = {'genes': genes,
                           'feature_names': profiles,
                           'features': features,
                           'association': association,
                           'source': 'jax_trials',
                           'jax_trial': evidence}
    yield feature_association


def harvest_and_convert(genes):
    """ get data from jax, convert it to ga4gh and return via yield """
    for jax_evidence in harvest(genes):
        # print "harvester_yield {}".format(jax_evidence.keys())
        for feature_association in convert(jax_evidence):
            # print "jax convert_yield {}".format(feature_association.keys())
            yield feature_association


def _parse(molecular_profile):
    """ returns gene, tuples[] """
    molecular_profile = molecular_profile.replace(' - ', '-')
    parts = molecular_profile.split()
    gene = None
    # gene_complete = True

    tuples = []
    tuple = None
    fusion_modifier = ''
    for idx, part in enumerate(parts):
        if not gene:
            gene = part
        # # deal with 'GENE - GENE '
        # if part == '-':
        #     gene += part
        #     gene_complete = False
        #     continue
        # elif not gene_complete:
        #     gene += part
        #     gene_complete = True
        #     continue

        if not tuple:
            tuple = []
        # build first tuple
        if len(tuples) == 0:
            if len(tuple) == 0 and '-' not in gene:
                tuple.append(gene)

        if idx == 0:
            continue

        # ignore standalone plus
        if not part == '+':
            tuple.append(part)

        # we know there is at least one more to fetch before terminating tuple
        if len(tuple) == 1 and idx < len(parts)-1:
            continue

        # is the current tuple complete?
        if (
                (len(tuple) > 1 and part.isupper()) or
                idx == len(parts)-1 or
                parts[idx+1].isupper()
           ):
                if len(tuple) == 1 and tuple[0].islower():
                    fusion_modifier = ' {}'.format(tuple[0])
                else:
                    tuples.append(tuple)
                tuple = None

    # if gene is a fusion, render genes separately
    if ('-' in gene):
        fusion = gene
        first_gene, second_gene = gene.split('-')
        tuples.append([first_gene, fusion + fusion_modifier])
        tuples.append([second_gene, fusion + fusion_modifier])
        gene = first_gene

    # if gene in tuples is fusion re-render
    def is_fusion(tuple):
        return '-' in tuple[0]

    non_fusion_tuples = [x for x in tuples if not is_fusion(x)]
    fusion_tuples = [x for x in tuples if is_fusion(x)]
    for tuple in fusion_tuples:
        fusion = tuple[0]
        first_gene, second_gene = fusion.split('-')
        non_fusion_tuples.append([first_gene, fusion])
        non_fusion_tuples.append([second_gene, fusion])
    tuples = non_fusion_tuples

    # get set of all genes
    genes = set([])
    for tuple in tuples:
        genes.add(tuple[0])

    return sorted(list(genes)), tuples


def _test():
    for feature_association in harvest_and_convert(None):
        print feature_association
        break
    # for jax_evidence in harvest([]):
    #     print '_test', jax_evidence
    #     break
    # exit(1)
    # for trial in harvest([]):
    #     print trial
    #     break


if __name__ == '__main__':
    import yaml
    import logging.config
    path = 'logging.yml'
    with open(path) as f:
        config = yaml.load(f)
    logging.config.dictConfig(config)

    _test()
