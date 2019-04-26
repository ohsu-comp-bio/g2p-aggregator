
import sys
import re
from lxml import html
from lxml import etree
import requests
import requests_cache
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from inflection import parameterize, underscore
import json
import logging
import evidence_label as el
import evidence_direction as ed

import cosmic_lookup_table

LOOKUP_TABLE = None
gene_list = None

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# see https://ckb.jax.org/about/curationMethodology


def _parse_profile(profile):
    parts = profile.split()
    global LOOKUP_TABLE
    global gene_list
    if not LOOKUP_TABLE:
        LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup()
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
        # Should only hit this if there's no mutation listed for
        # the present gene,
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
    """ get data from jax """
    for trial_info in _get_trials_ids():
        for jax_evidence in get_evidence([trial_info]):
            yield jax_evidence


def _get_trials_ids():
    """gets json for list of all trials yield"""
    offset = 0
    while True:
        url = 'https://ckb.jax.org/ckb-app/api/v1/clinicalTrials?offset={}&max=100'.format(offset)  # NOQA
        with requests_cache.disabled():
            page = requests.get(url, verify=False)
        trials_ids = []
        payload = page.json()
        logging.info('totalCount:{} offset:{}'.format(
            payload['totalCount'], offset))
        trials_infos = payload['clinicalTrials']
        if len(trials_infos) == 0:
            break
        offset = offset + 100
        for trial_info in trials_infos:
            yield {'id': trial_info['nctId'], 'trial': trial_info}


def get_evidence(trial_infos):
    """ scrape api """
    for trial_info in trial_infos:
        url = 'https://ckb.jax.org/ckb-app/api/v1/clinicalTrials/{}'.format(trial_info['id'])  # NOQA
        with requests_cache.disabled():
            try:
                page = requests.get(url, verify=False)
            except requests.ConnectionError as e:
                logging.warn(e)
                continue
        clinicalTrial = page.json()
        if clinicalTrial['variantRequirements'] == 'no' or len(clinicalTrial['variantRequirementDetails']) == 0:  # NOQA
            logging.info('no variants, skipping {}'.format(trial_info['id']))
            break
        yield {'jax_id': trial_info['id'], 'evidence': clinicalTrial}  # NOQA


def convert(jax_evidence):
    global LOOKUP_TABLE
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

        # Parse molecular profile and use for variant-level information.
        profile = profile.replace('Tp53', 'TP53').replace(' - ', '-')
        gene_index, mut_index, biomarkers, fusions = _parse_profile(profile)
        if not (len(gene_index) == len(mut_index) == len(biomarkers)):
            print "ERROR: This molecular profile has been parsed incorrectly!"
            print json.dumps({"molecular_profile": profile}, indent=4, sort_keys=True)  # NOQA

        else:
            parts = profile.split()
            for i in range(len(gene_index)):
                feature = {}
                feature['geneSymbol'] = gene_index[i]
                feature['name'] = ' '.join([gene_index[i], mut_index[i],
                                            biomarkers[i]])
                if biomarkers[i]:
                    feature['biomarker_type'] = biomarkers[i]

                # Look up variant and add position information.
                if not LOOKUP_TABLE:
                    LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                                   "./cosmic_lookup_table.tsv")
                matches = LOOKUP_TABLE.get_entries(gene_index[i], mut_index[i])
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
            for fusion in fusions:
                for gene in fusion:
                    feature = {}
                    feature['geneSymbol'] = gene
                    feature['name'] = '-'.join(fusion)
                    feature['biomarker_type'] = 'fusion'
                    features.append(feature)

    association = {}
    association['description'] = evidence['title']
    association['environmentalContexts'] = []
    for therapy in evidence['therapies']:
        association['environmentalContexts'].append({
            'description': therapy['therapyName']})
    association['phenotypes'] = []
    for indication in evidence['indications']:
        s = { 'description' : indication['name'],
              'id' : '{}:{}'.format(indication['source'], indication['id']) }
        association['phenotypes'].append(s)

    association['evidence'] = [{
        "evidenceType": {
            "sourceName": "jax-trials"
        },
        'description': evidence['title'],
        'info': {
            'publications': [
                'https://clinicaltrials.gov/ct2/show/{}'.format(jax)]
        }
    }]
    # add summary fields for Display
    association['evidence_label'] = 'D'
    feature_association = {'genes': genes,
                           'feature_names': profiles,
                           'features': features,
                           'association': association,
                           'source': 'jax_trials',
                           'jax_trials': evidence}
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
