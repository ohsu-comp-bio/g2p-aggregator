
import requests
import json
import os
import evidence_label as el
import evidence_direction as ed
import logging
import mutation_type as mut
from warnings import warn

resourceURLs = {
    "assertions": "/v2/assertion/search"
}
mmService = "http://api.molecularmatch.com"


apiKey = os.environ.get('MOLECULAR_MATCH_API_KEY')

# DEFAULT_GENES = []

HASH_KEYS = []

# with open("gene_symbols.txt") as f:
#     content = f.readlines()
# DEFAULT_GENES = [x.strip() for x in content]


def get_evidence():
    """ load from remote api """
    if not apiKey:
        raise ValueError('Please set MOLECULAR_MATCH_API_KEY in environment')
    # if not gene_ids:
    #     gene_ids = DEFAULT_GENES
    # first look for all drugs that impact this gene
    count = 0
    start = 0
    limit = 20
    url = mmService + resourceURLs["assertions"]
    filters = [{'facet': 'CONDITION',
                'term': 'CANCER',
                }]
    while start >= 0:
        payload = {
            'apiKey': apiKey,
            'limit': limit,
            'start': start,
            'filters': json.dumps(filters)
        }
        try:
            logging.info('%s %s', url, json.dumps(payload))
            r = requests.post(url, data=payload)
            assertions = r.json()
            if assertions['total'] == 0:
                start = -1
                continue
            else:
                start = start + limit
            logging.info(
                "page {} of {}. total {} count {}".format(
                    assertions['page'],
                    assertions['totalPages'],
                    assertions['total'],
                    count
                    )
            )
            # filter those drugs, only those with diseases
            for hit in assertions['rows']:
                # # do not process rows without drugs
                # if len(hit['therapeuticContext']) > 0:
                #     yield hit

                # # do not process rows that do not match our query
                # returned_gene = None
                # for tag in hit['tags']:
                #     if tag['facet'] == 'GENE':
                #         returned_gene = tag['term']
                # if returned_gene == gene:
                #     yield hit
                # else:
                #     raise ValueError(
                #         'evidence for {}, not {} - skipping'.format(
                #             returned_gene,
                #             gene
                #         )
                #     )

                # process all rows
                count = count + 1
                if not hit['hashKey'] in HASH_KEYS:
                    HASH_KEYS.append(hit['hashKey'])
                    yield hit
                else:
                    logging.info('duplicate: {}'.format(hit['hashKey']))

        except Exception as e:
            logging.error(
                "molecularmatch error fetching {}".format('CANCER'),
                exc_info=1
            )
            start = -1


def convert(evidence):
    """

    """
    if 'tier' not in evidence:
        logging.error('No tier?')
        logging.error(evidence.keys())

    sources = evidence['sources']
    tier = evidence.get('tier')
    direction = evidence['direction']
    narrative = evidence['narrative']

    # if len(evidence['mutations']) > 1:
    #     warn('Unexpected; two mutations in one entry; please check')
    # mutations = evidence['mutations'][0]
    therapeuticContext = evidence['therapeuticContext']
    clinicalSignificance = evidence['clinicalSignificance']
    tags = evidence['tags']
    gene = None
    condition = None
    mutation = None
    for tag in tags:
        if tag['facet'] == 'GENE' and tag['priority'] == 1:
            gene = tag['term']
        if tag['facet'] == 'CONDITION' and tag['priority'] == 1:
            condition = tag['term']
        if tag['facet'] == 'MUTATION' and tag['priority'] == 1:
            mutation = tag['term']
        if tag['facet'] == 'PHRASE' and 'ISOFORM EXPRESSION' in tag['term']:
            mutation = tag['term']

    if not gene:
        for tag in tags:
            if tag['facet'] == 'GENE':
                gene = tag['term']

    features = []
    for mutation_evidence in evidence['mutations']:
        feature = {}

        # mmatch uses location as a key, this in turn causes a field explosion
        # in ES since we are analysing all keys
        if 'wgsaData' in mutation_evidence:
            locations = []
            wgsaData = mutation_evidence['wgsaData']
            for idx, key in enumerate(wgsaData.keys()):
                wgsaData[key]['_key'] = key
                locations.append(wgsaData[key])
                del wgsaData[key]
            wgsaData['locations'] = locations

        feature['geneSymbol'] = gene
        feature['name'] = mutation
        feature['description'] = '{} {}'.format(gene, mutation)


        # Add variant-level information.
        # TODO: only looks at first location, not all locations.
        if ('GRCh37_location' in mutation_evidence and
                len(mutation_evidence['GRCh37_location']) > 0):
            grch37_mutation = mutation_evidence['GRCh37_location'][0]
            feature['referenceName'] = 'GRCh37'
            if 'ref' in grch37_mutation:
                feature['ref'] = grch37_mutation['ref']
            if 'alt' in grch37_mutation:
                feature['alt'] = grch37_mutation['alt']
            if 'chr' in grch37_mutation:
                feature['chromosome'] = str(grch37_mutation['chr'])
            if 'start' in grch37_mutation and grch37_mutation['start']:
                feature['start'] = int(grch37_mutation['start'])
            if 'stop' in grch37_mutation and grch37_mutation['stop']:
                feature['end'] = int(grch37_mutation['stop'])

        biomarker_types = []
        if 'mutation_type' in mutation_evidence:
            for mutation_type in mutation_evidence['mutation_type']:
                if 'Fusion' in mutation_type:
                    biomarker_types.append('fusion')
                elif ('Insertion' in mutation_type or 'Deletion' in mutation_type) and len(feature.get('ref', '')) < len(feature.get('alt', '')):  # NOQA
                    biomarker_types.append('insertion')
                elif ('Insertion' in mutation_type or 'Deletion' in mutation_type) and len(feature.get('alt', '')) < len(feature.get('ref', '')):  # NOQA
                    biomarker_types.append('deletion')
                else:
                    biomarker_types.append(mutation_type)
            biomarker_types = list(set(biomarker_types))
            if len(biomarker_types) != 0:
                feature['biomarker_type'] = ','.join(biomarker_types)
        features.append(feature)

    # if len(mutations['mutation_type']) == 1:
    #     feature['biomarker_type'] = mut.norm_biomarker(mutations['mutation_type'][0])
    # elif 'Fusion' in mutations['mutation_type']:
    #     feature['biomarker_type'] = 'fusion'
    # elif ('Insertion' in mutations['mutation_type'] or 'Deletion' in mutations['mutation_type']) and len(feature['ref']) < len(feature['alt']):
    #     feature['biomarker_type'] = 'insertion'
    # elif ('Insertion' in mutations['mutation_type'] or 'Deletion' in mutations['mutation_type']) and len(feature['alt']) < len(feature['ref']):
    #     feature['biomarker_type'] = 'deletion'
    # else:
    #     feature['biomarker_type'] = mut.norm_biomarker('NA')

    # create a drug label that normalization will process
    drug_names = []
    for tc in therapeuticContext:
        drug_names.append(tc['name'])
    drug_label = '+'.join(drug_names)

    association = {}
    association['description'] = narrative
    association['variant_name'] = []
    for v in evidence['variantInfo']:
        for l in v['locations']:
            if 'amino_acid_change' in l:
                association['variant_name'].append(l['amino_acid_change'])
    association['environmentalContexts'] = []
    association['environmentalContexts'].append({
        'description': drug_label})
    association['phenotype'] = {
        'description': condition
    }

    pubs = []
    for p in sources:
        pubs.append(p['link'])

    association['evidence'] = [{
        "evidenceType": {
            "sourceName": "molecularmatch"
        },
        'description': narrative,
        'info': {
            'publications': pubs
        }
    }]
    # add summary fields for Display

    # association['evidence_label'] = direction
    association = el.evidence_label(tier, association, na=False)
    association = ed.evidence_direction(tier, association, na=False)

    if len(pubs) > 0:
        association['publication_url'] = pubs[0]
    association['drug_labels'] = drug_label

    genes = []
    for mutation_evidence in evidence['mutations']:
        geneSymbol = mutation_evidence['geneSymbol']
        if geneSymbol not in genes:
            genes.append(geneSymbol)

    if (mutation):
        genes_from_features, ignore = _parse(mutation)
    else:
        genes_from_features, minimal_features = _parse(gene)
        if len(features) == 0:
            for feature_tuple in minimal_features:
                feature = {}
                feature['geneSymbol'] = feature_tuple[0]
                feature['description'] = feature['geneSymbol']

                if not feature['geneSymbol'].isupper() and len(genes) > 0:
                    feature['geneSymbol'] = genes[0]
                try:
                    feature['name'] = feature_tuple[1]

                except IndexError:
                    pass
                features.append(feature)

    if len(genes) == 0:
        genes = genes_from_features

    feature_association = {'genes': genes,
                           'features': features,
                           'feature_names': mutation,
                           'association': association,
                           'source': 'molecularmatch',
                           'molecularmatch': evidence}
    yield feature_association


def harvest(genes=None):
    """ get data from mm, ignores genes. gets all evidence for CANCER """
    for evidence in get_evidence():
        yield evidence


def harvest_and_convert(genes):
    """ get data from mm, convert it to ga4gh and return via yield """
    for evidence in harvest(genes):
        # print "harvester_yield {}".format(evidence.keys())
        # print evidence
        for feature_association in convert(evidence):
            # print "mm convert_yield {}".format(feature_association.keys())
            yield feature_association


def _parse(mutation):
    """ given a mutation expression, return array of genes and tuples """
    if not mutation:
        return [], []
    parts = mutation.split()
    if not parts[0].isupper():
        parts = parts[::-1]

    if '-' in parts[0]:
        genes = sorted(parts[0].split('-'))
    else:
        if parts[0].isupper():
            genes = [parts[0]]
        else:
            genes = [mutation.split()[0]]
            parts = mutation.split()

    tuples = []
    for gene in genes:
        if len(parts[1:]) > 0:
            tuples.append([gene, ' '.join(parts[1:])])
        else:
            tuples.append([gene])
    return genes, tuples


def _test():
    # gene_ids = ["CCND1", "CDKN2A", "CHEK1", "DDR2", "FGF19", "FGF3",
    #  "FGF4", "FGFR1", "MDM4", "PALB2", "RAD51D"]
    gene_ids = None
    for feature_association in harvest_and_convert(gene_ids):
        print feature_association.keys()
        print json.dumps(feature_association, indent=2)
        break

    # for evidence in harvest(gene_ids):
    #     #print evidence['narrative']
    #     print json.dumps(evidence, indent=2)
    #     break

if __name__ == '__main__':
    _test()
