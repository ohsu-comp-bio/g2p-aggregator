import requests
import re
import logging
import json
import copy

import hgvs.location
import hgvs.posedit
import hgvs.edit
from hgvs.sequencevariant import SequenceVariant
from feature_enricher import enrich


def _complement(bases):
    """
    return complement of bases string
    """
    complements = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    return ''.join([complements.get(base, base) for base in bases])


def _get_ref_alt(description):
    """
    parse ref & alt from description
    return none if no match
    """
    p = ".*[c]\.[0-9]*_[0-9]*(.*)"
    m = re.match(p, description)
    if m and len(m.groups()) == 1:
        return m.groups()[0]
    p = ".*[A-Z][0-9]*_[A-Z][0-9]*(.*)"
    m = re.match(p, description)
    if m and len(m.groups()) == 1:
        return m.groups()[0]
    return None


def allele_registry(hgvs):
    """
    call allele registry with hgvs notation, return allele_registry
    """
    url = 'http://reg.genome.network/allele?hgvs={}' \
        .format(requests.utils.quote(hgvs))
    r = requests.get(url, headers={'Accept': 'application/json'})
    if r.status_code not in [200, 400, 404]:
        logging.info('unexpected allele_registry {} {}'.format(url,
                                                               r.status_code))
    rsp = r.json()
    return rsp, url


def genomic_hgvs(feature, complement=False, description=False):
    """
    given a feature, create a hgvs genomic representation
    http://varnomen.hgvs.org/bg-material/refseq/#DNAg
    """
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
    ac = ac_map[feature['chromosome']]

    start = None
    end = None
    start_i = None
    end_i = None
    if 'start' in feature:
        start_i = int(feature['start'])
        start = hgvs.location.SimplePosition(
                base=start_i)
    if 'end' in feature:
        end_i = int(feature['end'])
        end = hgvs.location.SimplePosition(
              base=end_i)

    iv = None
    if start_i == end_i:
        iv = hgvs.location.Interval(start=start)
    else:
        iv = hgvs.location.Interval(start=start, end=end)

    # Make an edit object
    ref = feature.get('ref', None)
    if ref == '-':
        ref = None
    alt = feature.get('alt', None)
    if alt == '-':
        alt = None

    if complement:
        ref = _complement(ref)
        alt = _complement(alt)

    feature_description = feature.get('description', feature.get('name', None))

    edit = hgvs.edit.NARefAlt(ref=ref, alt=alt)

    posedit = hgvs.posedit.PosEdit(pos=iv, edit=edit)

    if description:
        # override with ref_alt from description or name
        # override edit if we have a hint from description that its a dup
        ref_alt = _get_ref_alt(feature_description)
        posedit.edit = ref_alt
    else:
        if 'dup' in feature_description:
            ref_alt = _get_ref_alt(feature_description)
            if ref_alt:
                posedit.edit = ref_alt + alt

    # Make the variant
    var = SequenceVariant(ac=ac, type='g', posedit=posedit)
    # https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh37.p13
    try:
        return str(var)
    except Exception as e:
        return None


def normalize(feature):
    if 'referenceName' not in feature or \
       'chromosome' not in feature or 'ref' not in feature:
            return None, None
    if feature['chromosome'] == 'None' or feature['chromosome'] is None:
        return None, None
    if feature['ref'] == 'None' or feature['ref'] is None:
        return None, None

    hgvs = genomic_hgvs(feature)
    allele = None
    provenance = None
    if hgvs:
        (allele, provenance) = allele_registry(hgvs)
        if ('errorType' in allele and
                allele['errorType'] == 'IncorrectReferenceAllele'):
            message = allele['message']
            actualAllele = allele['actualAllele']

            complement_ref = _complement(feature['ref'])
            if complement_ref == actualAllele:
                # print 'reverse strand re-try'
                hgvs = genomic_hgvs(feature, complement=True)
                (allele, provenance) = allele_registry(hgvs)
            # else:
            #     print 'complement_ref {} m[0] {}'.format(complement_ref,
            #                                              actualAllele)

        if ('errorType' in allele and
                allele['errorType'] == 'IncorrectHgvsPosition'):
            # print 'position error re-try'
            hgvs = genomic_hgvs(feature, description=True)
            (allele, provenance) = allele_registry(hgvs)

        if allele:
            allele['hgvs_g'] = hgvs

    return allele, provenance


def _apply_allele_registry(feature, allele_registry, provenance):
    # there is a lot of info in registry, just get synonyms and links
    links = feature.get('links', [])
    synonyms = feature.get('synonyms', [])
    links.append(allele_registry['@id'])
    if 'externalRecords' in allele_registry:
        externalRecords = allele_registry['externalRecords']
        links = links + [externalRecords[r][0].get('@id')
                         for r in externalRecords
                         if '@id' in externalRecords[r][0]
                         ]
        synonyms = synonyms + [externalRecords[r][0].get('id')
                               for r in externalRecords
                               if 'id' in externalRecords[r][0]
                               ]

    if 'genomicAlleles' in allele_registry:
        genomicAlleles = allele_registry['genomicAlleles']
        for genomicAllele in genomicAlleles:
            synonyms = synonyms + genomicAllele['hgvs']
            links.append(genomicAllele['referenceSequence'])

    synonyms = list(set(synonyms))
    links = list(set(links))
    if len(synonyms) > 0:
        feature['synonyms'] = synonyms
    if len(links) > 0:
        feature['links'] = links
    if 'provenance' not in feature:
        feature['provenance'] = []
    feature['provenance'].append(provenance)


def _fix_location_end(feature):
    """ if end not present, set it based on start, ref & alt length"""
    end = feature.get('end', 0)
    start = feature.get('start', 0)
    ref_len = 0
    alt_len = 0
    if feature.get('ref', None):
        ref_len = len(feature.get('ref', ''))
    if feature.get('alt', None):
        alt_len = len(feature.get('alt', ''))
    offset = max(ref_len, alt_len)
    if start > 0 and end == 0:
        end = max(start, start + (offset - 1))
        feature['end'] = end
    return feature


def normalize_feature_association(feature_association):
    """ given the 'final' g2p feature_association,
    update it with genomic location """
    allele_registry = None
    normalized_features = []
    for feature in feature_association['features']:
        try:
            # ensure we have location, enrich can create new features
            enriched_features = enrich(copy.deepcopy(feature), feature_association)
            for enriched_feature in enriched_features:
                # go get AR info
                (allele_registry, provenance) = normalize(enriched_feature)
                if allele_registry:
                    if '@id' in allele_registry:
                        _apply_allele_registry(enriched_feature,
                                               allele_registry,
                                               provenance)
                enriched_feature = _fix_location_end(enriched_feature)
                normalized_features.append(enriched_feature)
            feature_association['features'] = normalized_features
        except Exception as e:
            logging.exception(
                'exception {} feature {} allele {}'.format(e, feature,
                                                           allele_registry))


def _test(feature):
    allele_registry = normalize(feature)[0]
    if allele_registry and '@id' not in allele_registry:
        print 'FAIL', allele_registry['message']
        print "\t", allele_registry['hgvs_g']
        print "\t", feature
        print "\t", allele_registry
    elif allele_registry:
        print 'OK', allele_registry['hgvs_g']
    else:
        print 'OK', 'not normalized'

if __name__ == '__main__':
    import yaml
    import logging.config
    path = 'logging.yml'
    with open(path) as f:
        config = yaml.load(f)
    logging.config.dictConfig(config)

    # _test('YAP1-MAMLD1 Fusion')
    # _test('YAP1-MAMLD1')
    _test({
      "entrez_id": 238,
      "end": 29445213,
      "name": "HIP1-ALK I1171N",
      "start": 29445213,
      "biomarker_type": "snp",
      "referenceName": "GRCh37",
      "geneSymbol": "ALK",
      "alt": "T",
      "ref": "A",
      "chromosome": "2"
    })

    _test({"end": "55242483",
           "name": "EGFR c.2237_2253delAATTAAGAGAAGCAACAinsTC",
           "start": "55242467", "biomarker_type": "snp",
           "referenceName": "GRCh37", "alt": "TC", "ref": "-",
           "chromosome": "7",
           "description": "EGFR c.2237_2253delAATTAAGAGAAGCAACAinsTC"})

    _test({"entrez_id": 9968, "end": 70349258, "name": "L1224F",
           "start": 70349258, "biomarker_type": "snp",
           "referenceName": "GRCh37", "geneSymbol": "MED12",
           "alt": "T", "ref": "C", "chromosome": "23"})

    _test({"name": "ABL1:V289I", "start": 133747558,
           "biomarker_type": "mutant", "referenceName": "GRCh37",
           "geneSymbol": "ABL1", "alt": "A", "ref": "G", "chromosome": "9",
           "description": "ABL1:I242T,M244V,K247R,L248V,G250E,G250R,Q252R,Q252H,Y253F,Y253H,E255K,E255V,M237V,E258D,W261L,L273M,E275K,E275Q,D276G,T277A,E279K,V280A,V289A,V289I,E292V,E292Q,I293V,L298V,V299L,F311L,F311I,T315I,F317L,F317V,F317I,F317C,Y320C,L324Q,Y342H,M343T,A344V,A350V,M351T,E355D,E355G,E355A,F359V,F359I,F359C,F359L,D363Y,L364I,A365V,A366G,L370P,V371A,E373K,V379I,A380T,F382L,L384M,L387M,L387F,L387V,M388L,Y393C,H396P,H396R,H396A,A397P,S417F,S417Y,I418S,I418V,A433T,S438C,E450K,E450G,E450A,E450V,E453K,E453G,E453A,E453V,E459K,E459G,E459A,E459V,M472I,P480L,F486S,E507G"})  # NOQA

    _test({"end": 28592642, "name": "FLT3 D835N", "referenceName": "GRCh37",
           "start": 28592642, "biomarker_type": "snp", "geneSymbol": "FLT3",
           "attributes": {"amino_acid_change": {"string_value": "D835N"},
                            "germline": {"string_value": None},
                            "partner_gene": {"string_value": None},
                            "cytoband": {"string_value": None},
                            "exons": {"string_value": "20"},
                            "notes": {"string_value": None},
                            "cosmic": {"string_value": "789"},
                            "effect": {"string_value": None},
                            "cnv_type": {"string_value": None},
                            "id": {"string_value": 139},
                            "variant_type": {"string_value": "missense"},
                            "dna_change": {"string_value": "2503G>A"},
                            "codons": {"string_value": "835"},
                            "chromosome_based_cnv": {"string_value": False},
                            "transcript": {"string_value": "ENST00000241453"},
                            "description_type": {"string_value": "HGVS"},
                            "chromosome": {"string_value": None},
                            "description": {"string_value": None}},
          "alt": "A", "ref": "G", "chromosome": "13"})

    _test({"end": "55592183", "name": "KIT p.S501_A502dup",
           "start": "55592183",
           "biomarker_type": "polymorphism", "referenceName": "GRCh37",
           "alt": "CTGCCT", "ref": "-", "chromosome": "4",
           "description": "KIT p.S501_A502dup"})

    _test({"end": "37880996", "name": "ERBB2 Y772_A775dup",
           "start": "37880995",
           "biomarker_type": "nonsense", "referenceName": "GRCh37",
           "alt": "ATACGTGATGGC", "ref": "-", "chromosome": "17",
           "description": "ERBB2 Y772_A775dup"})

    _test({"end": 140453136, "name": "BRAF V600E", "referenceName": "GRCh37",
           "start": 140453136, "biomarker_type": "snp", "geneSymbol": "BRAF",
           "attributes": {"amino_acid_change": {"string_value": "V600E"},
                          "germline": {"string_value": None},
                          "partner_gene": {"string_value": None},
                          "cytoband": {"string_value": None},
                          "exons": {"string_value": "15"},
                          "notes": {"string_value": None},
                          "cosmic": {"string_value": "476"},
                          "effect": {"string_value": None},
                          "cnv_type": {"string_value": None},
                          "id": {"string_value": 112},
                          "variant_type": {"string_value": "missense"},
                          "dna_change": {"string_value": "1799T>A"},
                          "codons": {"string_value": "600"},
                          "chromosome_based_cnv": {"string_value": False},
                          "transcript": {"string_value": "ENST00000288602"},
                          "description_type": {"string_value": "HGVS"},
                          "chromosome": {"string_value": None},
                          "description": {"string_value": None}},
           "alt": "A", "ref": "T", "chromosome": "7"})

    # _test({"end": 1806125, "name": "FGFR3 F384L", "referenceName": "GRCh37", "start": 1806125, "biomarker_type": "snp", "geneSymbol": "FGFR3", "attributes": {"amino_acid_change": {"string_value": "F384L"}, "germline": {"string_value": False}, "partner_gene": {"string_value": None}, "cytoband": {"string_value": None}, "exons": {"string_value": "9"}, "notes": {"string_value": None}, "cosmic": {"string_value": None}, "effect": {"string_value": None}, "cnv_type": {"string_value": None}, "id": {"string_value": 391}, "variant_type": {"string_value": "missense"}, "dna_change": {"string_value": "1150T>C"}, "codons": {"string_value": "384"}, "chromosome_based_cnv": {"string_value": False}, "transcript": {"string_value": "ENST00000340107"}, "description_type": {"string_value": "HGVS"}, "chromosome": {"string_value": None}, "description": {"string_value": None}}, "alt": "C", "ref": "T", "chromosome": "4"})

    _test( {"entrez_id": 1956, "end": None, "name": "R776C", "start": None, "referenceName": "GRCh37", "geneSymbol": "EGFR", "alt": "None", "ref": "None", "chromosome": "None"})


    _test({"end": "55242478", "description": "EGFR E746_E749delELRE", "links": ["https://api.molecularmatch.com/v2/mutation/get?name=EGFR+E746_E749delELRE"], "start": "55242467", "biomarker_type": "nonsense", "referenceName": "GRCh37", "alt": "-", "ref": "12", "chromosome": "7", "name": "EGFR E746_E749delELRE"})
