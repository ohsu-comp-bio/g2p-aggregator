#!/usr/bin/python

# given a set of features, query g2p, report findings

import g2p_client
from collections import Counter
import re

# produced by harvester/query_generator
patient_features = [{'description': '', 'start': 27100988L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'ARID1A', 'alt': 'T', 'ref': 'C', 'chromosome': '1', 'name': 'ARID1A '}, {'description': '', 'start': 204494718L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'MDM4', 'alt': 'G', 'ref': 'C', 'chromosome': '1', 'name': 'MDM4 '}, {'description': '', 'start': 30143341L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'ALK', 'alt': 'A', 'ref': 'G', 'chromosome': '2', 'name': 'ALK '}, {'description': '', 'start': 48028096L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'MSH6', 'alt': 'C', 'ref': 'G', 'chromosome': '2', 'name': 'MSH6 '}, {'description': '', 'start': 10084764L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'FANCD2', 'alt': 'G', 'ref': 'C', 'chromosome': '3', 'name': 'FANCD2 '}, {'description': '', 'start': 142185372L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'ATR', 'alt': 'G', 'ref': 'C', 'chromosome': '3', 'name': 'ATR '}, {'description': '', 'start': 178916923L, 'biomarker_type': 'indel', 'referenceName': 'GRCh37', 'geneSymbol': 'PIK3CA', 'alt': 'C', 'ref': 'CCAGTAG', 'chromosome': '3', 'name': 'PIK3CA '}, {'description': '', 'start': 117647566L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'ROS1', 'alt': 'C', 'ref': 'G', 'chromosome': '6', 'name': 'ROS1 '}, {'description': '', 'start': 87285753L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'NTRK2', 'alt': 'G', 'ref': 'C', 'chromosome': '9', 'name': 'NTRK2 '}, {'description': '', 'start': 108106483L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'ATM', 'alt': 'C', 'ref': 'G', 'chromosome': '11', 'name': 'ATM '}, {'description': '', 'start': 45618180L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'FANCM', 'alt': 'G', 'ref': 'C', 'chromosome': '14', 'name': 'FANCM '}, {'description': '', 'start': 45644454L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'FANCM', 'alt': 'C', 'ref': 'G', 'chromosome': '14', 'name': 'FANCM '}, {'description': '', 'start': 2110733L, 'biomarker_type': 'substitution', 'referenceName': 'GRCh37', 'geneSymbol': 'TSC2', 'alt': 'G', 'ref': 'C', 'chromosome': '16', 'name': 'TSC2 '}, {'description': 'GAIN Copy Number Ratio 3.0528', 'start': 39771328L, 'biomarker_type': 'copy_number_variation', 'referenceName': 'GRCh37', 'geneSymbol': 'IDO1', 'alt': '', 'ref': '', 'chromosome': '8', 'name': 'IDO1 '}, {'description': 'GAIN Copy Number Ratio 5.3306', 'start': 39792474L, 'biomarker_type': 'copy_number_variation', 'referenceName': 'GRCh37', 'geneSymbol': 'IDO2', 'alt': '', 'ref': '', 'chromosome': '8', 'name': 'IDO2 '}, {'description': 'LOSS Copy Number Ratio 0.3497', 'start': 21967751L, 'biomarker_type': 'copy_number_variation', 'referenceName': 'GRCh37', 'geneSymbol': 'CDKN2A', 'alt': '', 'ref': '', 'chromosome': '9', 'name': 'CDKN2A '}, {'description': 'GAIN Copy Number Ratio 7.5539', 'start': 38268656L, 'biomarker_type': 'copy_number_variation', 'referenceName': 'GRCh37', 'geneSymbol': 'FGFR1', 'alt': '', 'ref': '', 'chromosome': '8', 'name': 'FGFR1 '}, {'description': 'LOSS Copy Number Ratio 0.5662', 'start': 89623195L, 'biomarker_type': 'copy_number_variation', 'referenceName': 'GRCh37', 'geneSymbol': 'PTEN', 'alt': '', 'ref': '', 'chromosome': '10', 'name': 'PTEN '}, {'description': 'GAIN Copy Number Ratio 2.883', 'start': 69455873L, 'biomarker_type': 'copy_number_variation', 'referenceName': 'GRCh37', 'geneSymbol': 'CCND1', 'alt': '', 'ref': '', 'chromosome': '11', 'name': 'CCND1 '}, {'description': 'GAIN Copy Number Ratio 2.0415', 'start': 128748315L, 'biomarker_type': 'copy_number_variation', 'referenceName': 'GRCh37', 'geneSymbol': 'MYC', 'alt': '', 'ref': '', 'chromosome': '8', 'name': 'MYC '}]  # NOQA


def print_top_results(features_of_interest):
    """ query ES for each feature using a variety of queries """
    location = g2p_client.location_query(features_of_interest)
    is_HG37 = re.compile('NC_.*\.10:g')
    for fa in location['feature_associations']:
        for f in fa['features']:
            for s in f.get('synonyms', []):
                if is_HG37.match(s):
                    print "************************"
                    print s
                    print "************************"

    g2p = g2p_client.G2PDatabase('localhost')
    for name in location['queries'].keys():
        qs = location['queries'][name]['query']['query_string']['query']
        r = g2p.raw_dataframe(query_string=qs, verbose=False)
        print name, 'number of hits {}'.format(len(r))
        publications_c = Counter()
        protein_effects_c = Counter()
        protein_domains_c = Counter()
        alleles_c = Counter()
        biomarkers_c = Counter()
        pathways_c = Counter()
        evidence_level_c = Counter()
        source_c = Counter()
        drugs_c = Counter()
        features = []
        protein_effects = []
        protein_domains = []
        biomarkers = []
        alleles = []
        pathways = []

        for fa in location['feature_associations']:
            for f in fa['features']:
                features.append(f)
                for pe in f.get('protein_effects', []):
                    protein_effects.append(pe)
                for pd in f.get('protein_domains', []):
                    protein_domains.append(pd['name'])
                for s in f.get('synonyms', []):
                    if is_HG37.match(s):
                        alleles.append(s)
                for pw in f.get('pathways', []):
                    pathways.append(pw)
                biomarkers.append('{} {}'.format(f['geneSymbol'],
                                                 f['biomarker_type']))
        pathways = list(set(pathways))
        protein_effects = list(set(protein_effects))
        protein_domains = list(set(protein_domains))
        alleles = list(set(alleles))

        for fa in r:
            for environmentalContext in fa['association'].get('environmentalContexts', []):
                drugs_c[environmentalContext['term']] += 1
            for ei in fa['association'].get('evidence', []):
                for p in ei['info']['publications']:
                    publications_c[p] += 1
            for protein_effect in protein_effects:
                protein_effect_suffix = protein_effect.split(':')[1]
                for f in fa['features']:
                    if protein_effect_suffix in [pe.split(':')[1] for pe in f.get('protein_effects', [])]:
                        protein_effects_c[protein_effect_suffix] += 1
            for protein_domain in protein_domains:
                for f in fa['features']:
                    if protein_domain in f.get('protein_domains', []):
                        protein_domains_c[protein_domain['name']] += 1
            for allele in alleles:
                for f in fa['features']:
                    if allele in f.get('synonyms', []):
                        alleles_c[allele] += 1
            for biomarker in biomarkers:
                for f in fa['features']:
                    b = '{} {}'.format(f.get('geneSymbol', None), f.get('biomarker_type', None))
                    if biomarker == b:
                        biomarkers_c[b] += 1
            for pw in pathways:
                for f in fa['features']:
                    if pw in f.get('pathways', []):
                        pathways_c[pw] += 1

            evidence_level_c[fa['association']['evidence_label']] += 1
            source_c[fa['source']] += 1

        print "    query", qs
        print "    top publication", publications_c.most_common(1)
        print "    top drug", drugs_c.most_common(1)
        print "    top allele", alleles_c.most_common(1)
        print "    top protein_effect", protein_effects_c.most_common(1)
        print "    top protein_domain", protein_domains_c.most_common(1)
        print "    top biomarker", biomarkers_c.most_common(1)
        print "    top pathway", pathways_c.most_common(1)
        print "    evidence_levels", evidence_level_c.most_common(4)
        print "    sources", source_c.most_common(4)

for f in patient_features:
    print_top_results([f])
