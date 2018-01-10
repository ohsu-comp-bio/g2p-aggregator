import sys
sys.path.append('.')  # NOQA
import json
from feature_enricher import enrich
from jax_trials import _parse_profile, convert
import cosmic_lookup_table
import mutation_type as mut

JAX_TRIAL = '{"indications": [{"source": "JAX", "id": 10000003, "name": "Advanced Solid Tumor"}, {"source": "DOID", "id": 2531, "name": "hematologic cancer"}], "title": "Safety Study of Oral MGCD265 Administered Without Interruption to Subjects With Advanced Malignancies", "gender": "both", "nctId": "NCT00697632", "sponsors": "MethylGene Inc.", "recruitment": "Recruiting", "variantRequirements": "yes", "updateDate": "08/31/2015", "phase": "Phase I", "variantRequirementDetails": [{"molecularProfile": {"profileName": "MET alterations", "id": 1112}, "requirementType": "partial"}, {"molecularProfile": {"profileName": "MET positive", "id": 1240}, "requirementType": "partial"}, {"molecularProfile": {"profileName": "MET amp", "id": 1629}, "requirementType": "partial"}], "therapies": [{"id": 809, "therapyName": "Glesatinib"}]}'  # NOQA


def test_feature_enrich_MET_AMP():
    """ ensure that the MM variant endpoint does not have a false positive """
    profile = 'MET amp'
    feature = enrich({'description': profile})
    assert 'start' not in feature


def test_convert():
    """ this particular piece of evidence has no genomic location """
    evidence = json.loads(JAX_TRIAL)
    feature_association = convert(
                            {'jax_id': 'foobar', 'evidence': evidence}).next()
    features = feature_association['features']
    assert len(features) == 3
    for feature in features:
        assert 'start' not in feature


def test_profiles():
    """
    https://github.com/ohsu-comp-bio/g2p-aggregator/blame/v0.7/harvester/jax_trials.py#L25
    """
    evidence = json.loads(JAX_TRIAL)
    LOOKUP_TABLE = None
    # this snippet of code is from jax_trials.convert
    genes = set([])
    profiles = []
    features = []
    for detail in evidence['variantRequirementDetails']:
        profileName = detail['molecularProfile']['profileName']
        genes.add(profileName.split(' ')[0])
        profiles.append(profileName)
    genes = list(genes)
    assert profiles == [u'MET alterations', u'MET positive', u'MET amp']
    assert genes == [u'MET']
    for profile in profiles:
        # Parse molecular profile and use for variant-level information.
        profile = profile.replace('Tp53', 'TP53').replace(' - ', '-')
        gene_index, mut_index, biomarkers, fusions = _parse_profile(profile)
        if not (len(gene_index) == len(mut_index) == len(biomarkers)):
            # for this test, change logging to raising an exception
            raise Exception("ERROR: This molecular profile "
                            "has been parsed incorrectly!")

        parts = profile.split()
        for i in range(len(gene_index)):
            feature = {}
            feature['geneSymbol'] = gene_index[i]
            feature['name'] = ' '.join([gene_index[i], mut_index[i],
                                        biomarkers[i]])
            if biomarkers[i]:
                feature['biomarker_type'] = mut.norm_biomarker(
                    biomarkers[i])
            else:
                feature['biomarker_type'] = mut.norm_biomarker('na')

            # Look up variant and add position information.
            if not LOOKUP_TABLE:
                LOOKUP_TABLE = cosmic_lookup_table.CosmicLookup(
                               "./cosmic_lookup_table.tsv")
            matches = LOOKUP_TABLE.get_entries(gene_index[i], mut_index[i])
            print 'profile >{}< gene_index[i] >{}< mut_index[i] >{}< matches {}'.format(
                                                            profile,
                                                            gene_index[i],
                                                            mut_index[i],
                                                            len(matches))
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
    assert len(features) == 3
