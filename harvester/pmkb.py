from __future__ import print_function
import json
import evidence_label as el
import evidence_direction as ed

def harvest(genes=None):
    with open("../data/pmkb_interpretations.json", "r") as ins:
        for line in ins:
            interpretations = json.loads(line)['interpretations']
            for interpretation in interpretations:
                if not genes:
                    yield interpretation
                else:
                    if interpretation['gene']['name'] in genes:
                        yield interpretation


def convert(interpretation):
    # for each interpretation
    association = {}
    genes = interpretation['gene']['name']
    variants = interpretation['variants']
    tumors = interpretation['tumors']

    features = []
    variant_name = []
    for variant in variants:
        c = variant.get('coordinates')
        feature = {}
        if c:
            coordinates = c.replace(' ', '').split(',')
            coordinate = coordinates[0]
            a = coordinate.split(':')
            chromosome = a[0]
            start, stop = a[1].split('-')
            feature['start'] = int(start)
            feature['end'] = int(stop)
            feature['chromosome'] = str(chromosome)

        feature['name'] = variant['name']
        feature['geneSymbol'] = variant['gene']['name']
        feature['referenceName'] = 'GRCh37/hg19'
        feature['biomarker_type'] = variant['variant_type']
        attributes = {}
        for key in variant.keys():
            if key not in ['coordinates', 'name', 'gene']:
                attributes[key] = {'string_value': variant[key]}
        feature['attributes'] = attributes

        # TODO - replace w/ biocommons/hgvs ?
        if 'dna_change' in variant:
            dna_change = variant['dna_change']
            if dna_change and '>' in dna_change:
                prefix, alt = dna_change.split('>')
                ref = prefix[-len(alt):]
                if len(ref) > 0 and len(alt) > 0:
                    feature['ref'] = ref
                    feature['alt'] = alt

        if attributes['amino_acid_change']['string_value']:
            variant_name.append(attributes['amino_acid_change']['string_value'])

        features.append(feature)

    association['source_link'] = 'https://pmkb.weill.cornell.edu/therapies/{}'.format(interpretation['id'])

    association = el.evidence_label(str(interpretation['tier']), association, na=True)
    association = ed.evidence_direction(str(interpretation['tier']), association, na=True)

    association['description'] = interpretation['interpretation']

    association['phenotypes'] = []
    for tumor in tumors:
        association['phenotypes'].append({ 'description': tumor['name'] })

    association['drug_labels'] = 'NA'
    association['evidence'] = [{
         "evidenceType": { "sourceName": "pmkb" },
         'description': str(interpretation['tier']),
         'info': {
             'publications': [
    #             'http://www.ncbi.nlm.nih.gov/pubmed/{}'.format(c['pmid']) for c in interpretation['citations']  # NOQA
             ]
         }
    }]

    association['publication_url'] = ''
    source_url = 'https://pmkb.weill.cornell.edu/therapies/{}'.format(interpretation['id'])
    feature_association = {
        'genes': [genes],
        'features': features,
        'feature_names': ', '.join(sorted([f['name'] for f in features])),
        'association': association,
        'source': 'pmkb',
        'source_url': source_url,
        'pmkb': {
            'variant': variants,
            'tumor': tumors,
            'tissues': interpretation['tissues']
    }}
    yield feature_association


def harvest_and_convert(genes):
    """ get data from pmkb, convert it to ga4gh and return via yield """
    for evidence in harvest(genes):
        for feature_association in convert(evidence):
            yield feature_association
