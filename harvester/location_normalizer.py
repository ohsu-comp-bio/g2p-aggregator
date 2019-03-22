import requests
import re
import logging
from xml.etree import ElementTree
import copy

import hgvs.location
import hgvs.posedit
import hgvs.edit
from hgvs.sequencevariant import SequenceVariant
from feature_enricher import enrich
import protein
from Bio.SeqUtils import seq1
import hgvs.parser

# expensive resource, create only once
HGVS_PARSER = hgvs.parser.Parser()


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


def hgvs_query_allele_registry(hgvs):
    """
    call allele registry with hgvs notation, return allele registry response and url
    """
    url = 'http://reg.genome.network/allele?hgvs={}' \
        .format(requests.utils.quote(hgvs))
    r = requests.get(url, headers={'Accept': 'application/json'})
    if r.status_code not in [200, 400, 404]:
        logging.info('unexpected allele_registry {} {}'.format(url,
                                                               r.status_code))
    rsp = r.json()
    return rsp, url


def construct_hgvs(feature, complement=False, description=False, exclude={}):
    """
    given a feature, create an hgvs representation
    http://varnomen.hgvs.org/bg-material/refseq/#DNAg
    http://varnomen.hgvs.org/bg-material/refseq/#proteinp
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

    pa = feature.get('protein_allele', False)

    if pa:
        start_i = int(feature.get('protein_start', '_-1')[1:])
        try:
            end_i = int(feature.get('protein_end', '_-1')[1:])
        except TypeError:
            end_i = -1
    else:
        start_i = int(feature.get('start', -1))
        end_i = int(feature.get('end', -1))

    # Make an edit object

    feature_description = feature.get('description', feature.get('name', None))

    if pa:
        ref = feature.get('protein_ref', None)
        alt = feature.get('protein_alt', None)
        var_type = feature['biomarker_type'].lower()
        if var_type == 'ins':
            edit = hgvs.edit.AARefAlt(alt=alt)
        else:
            edit = hgvs.edit.AARefAlt(ref=ref, alt=alt)
        hgvs_type = 'p'
        ac = protein.lookup_from_gene(
            feature['geneSymbol'],
            ref_start=feature.get('protein_start', None),
            ref_end=feature.get('protein_end', None),
            exclude=exclude
        )
    else:
        ref = feature.get('ref', None)
        if ref == '-':
            ref = None
        alt = feature.get('alt', None)
        if alt == '-':
            alt = None

        if complement:
            ref = _complement(ref)
            alt = _complement(alt)

        edit = hgvs.edit.NARefAlt(ref=ref, alt=alt)
        hgvs_type = 'g'
        if feature.get('referenceName') == '37':
            feature['referenceName'] = 'GRCh37'
        assert feature.get('referenceName') == 'GRCh37',  'should be GRCh37? was {}'.format(feature.get('referenceName'))
        ac = ac_map[feature['chromosome']]

    if pa:
        if start_i > -1:
            start = hgvs.location.AAPosition(
                base=start_i,
                aa=feature['protein_start'][0]
            )
        else:
            start = None
        if end_i > -1:
            end = hgvs.location.AAPosition(
                base=end_i,
                aa=feature['protein_end'][0]
            )
        elif var_type == 'ins':
            end = hgvs.location.AAPosition(
                aa=protein.fasta[ac][start_i],
                base=start_i + 1
            )
        else:
            end = None
    else:
        if start_i > -1:
            start = hgvs.location.SimplePosition(
                base=start_i
            )
        else:
            start = None
        if end_i > -1:
            end = hgvs.location.SimplePosition(
                base=end_i
            )
        else:
            end = None

    if start_i == end_i:
        iv = hgvs.location.Interval(start=start)
    else:
        iv = hgvs.location.Interval(start=start, end=end)

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
    var = SequenceVariant(ac=ac, type=hgvs_type, posedit=posedit)
    # https://www.ncbi.nlm.nih.gov/grc/human/data?asm=GRCh37.p13
    try:
        return str(var)
    except Exception as e:
        return None


def _get_feature_attr(feature, attr):
    r = feature.get(attr, None)
    if not r:
        r = None
    elif r.lower().strip() == 'none':
        r = None
    feature[attr] = r
    return r


def normalize(feature):

    if feature.get('protein_allele', False):
        start = _get_feature_attr(feature, 'protein_start')
        if not start:
            return None, None
    else:
        ref_assembly = _get_feature_attr(feature, 'referenceName')
        chr = _get_feature_attr(feature, 'chromosome')
        ref = _get_feature_attr(feature, 'ref')
        alt = _get_feature_attr(feature, 'alt')

        if ref_assembly is None or chr is None:
            return None, None

        if ref is None and alt is None:
            return None, None

    hgvs = construct_hgvs(feature)
    allele = None
    provenance = None
    if hgvs:
        (allele, provenance) = hgvs_query_allele_registry(hgvs)
        if ('errorType' in allele and
                allele['errorType'] == 'IncorrectReferenceAllele'):
            message = allele['message']
            actualAllele = allele['actualAllele']

            complement_ref = _complement(feature['ref'])
            if complement_ref == actualAllele:
                # print 'reverse strand re-try'
                hgvs = construct_hgvs(feature, complement=True)
                (allele, provenance) = hgvs_query_allele_registry(hgvs)
            # else:
            #     print 'complement_ref {} m[0] {}'.format(complement_ref,
            #                                              actualAllele)

        if ('errorType' in allele and
                allele['errorType'] == 'IncorrectHgvsPosition'):
            # print 'position error re-try'
            hgvs = construct_hgvs(feature, exclude={hgvs.split(':')[0],})
            (allele, provenance) = hgvs_query_allele_registry(hgvs)

        if ('errorType' in allele and
                allele['errorType'] == 'IncorrectHgvsPosition'):
            # print 'position error re-try'
            hgvs = construct_hgvs(feature, description=True)
            (allele, provenance) = hgvs_query_allele_registry(hgvs)

    return allele, provenance


def _get_clingen_xrefs(clinvar_alleles):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={}[alleleid]'.format(
        ','.join(clinvar_alleles)
    )
    resp = requests.get(url)
    resp.raise_for_status()
    tree = ElementTree.fromstring(resp.content)
    variant_ids = [x.text for x in tree.find('IdList')]
    clingen_alleles = set()
    for variant_id in variant_ids:
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=clinvar&id={}&rettype=variation'.format(variant_id)
        resp = requests.get(url)
        resp.raise_for_status()
        tree = ElementTree.fromstring(resp.content)
        xreflist = tree.find('VariationReport').find('Allele').find('XRefList')
        clingen_alleles.update(
            set([x.get('ID') for x in xreflist if x.get('DB') == 'ClinGen'])
        )
    return clingen_alleles


def _collect_metadata(feature, allele_registry):
    links = feature.get('links', [])
    synonyms = feature.get('synonyms', [])
    clinvar_alleles = set()
    links.append(allele_registry['@id'])
    if 'externalRecords' in allele_registry:
        externalRecords = allele_registry['externalRecords']
        for source, eRecord in externalRecords.items():
            for r in eRecord:
                if '@id' in r:
                    links.append(r['@id'])
                if 'id' in r:
                    synonyms.append(r['id'])
                if source == 'ClinVarAlleles':
                    clinvar_alleles.add(str(r['alleleId']))

    if 'genomicAlleles' in allele_registry:
        genomicAlleles = allele_registry['genomicAlleles']
        for genomicAllele in genomicAlleles:
            synonyms = synonyms + genomicAllele['hgvs']
            links.append(genomicAllele['referenceSequence'])

    if 'transcriptAlleles' in allele_registry:
        transcriptAlleles = allele_registry['transcriptAlleles']
        for transcriptAllele in transcriptAlleles:
            synonyms = synonyms + transcriptAllele['hgvs']
            if 'proteinEffect' in transcriptAllele:
                proteinEffect = transcriptAllele['proteinEffect']
                if 'hgvs' in proteinEffect:
                    synonyms.append(proteinEffect['hgvs'])
                if 'hgvsWellDefined' in proteinEffect:
                    synonyms.append(proteinEffect['hgvsWellDefined'])

    return {
        'links': links,
        'synonyms': synonyms,
        'clinvar_alleles': clinvar_alleles
    }


def _fetch_allele_registry(allele):
    url = 'http://reg.genome.network/allele/{}'.format(allele)
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def _apply_allele_registry(feature, allele_registry, provenance):
    # there is a lot of info in registry, just get synonyms and links
    extract = _collect_metadata(feature, allele_registry)
    synonyms = set(extract['synonyms'])
    links = set(extract['links'])
    if 'provenance' not in feature:
        feature['provenance'] = []
    feature['provenance'].append(provenance)
    pa = feature.get('protein_allele', False)
    if pa:
        clingen_alleles = _get_clingen_xrefs(extract['clinvar_alleles'])
        for allele in clingen_alleles:
            allele_registry = _fetch_allele_registry(allele)
            extract = _collect_metadata(feature, allele_registry)
            synonyms.update(extract['synonyms'])
            links.update(extract['links'])

    if len(synonyms) > 0:
        feature['synonyms'] = list(synonyms)
        hgvs_g = set()
        hgvs_p = set()
        for synonym in feature.get('synonyms', []):
            if not ('g.' in synonym or 'p.' in synonym):
                continue
            try:
                hgvs_variant = HGVS_PARSER.parse_hgvs_variant(synonym)
            except Exception as e:
                print(str(e))
                continue
            if hgvs_variant.type == 'p':
                hgvs_p.add(hgvs_variant.format().split(':')[1])
                hgvs_p.add(hgvs_variant.format(conf={"p_3_letter": False}).split(':')[1])
            if hgvs_variant.type == 'g':
                hgvs_g.add(hgvs_variant.format().split(':')[1])
        feature['hgvs_g_suffix'] = list(hgvs_g)
        feature['hgvs_p_suffix'] = list(hgvs_p)

    if len(links) > 0:
        feature['links'] = list(links)


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


def _test(feature, expected_hgvs=''):
    if feature.get('protein_allele', False):
        feature = enrich(feature, None)[0]
    ar, q = normalize(feature)
    if ar:
        _apply_allele_registry(feature, ar, q)
        hgvs = feature.get('synonyms', [])
        if '@id' not in ar:
            print 'FAIL', ar['message']
            print "\t", ', '.join(hgvs)
            print "\t", feature
            print "\t", ar
        elif expected_hgvs and expected_hgvs not in hgvs:
            print 'FAIL', 'expected hgvs not found in synonyms'
            print "\t", q
            print "\t", ', '.join(hgvs)
            print "\t", expected_hgvs
        else:
            print 'OK'
    elif expected_hgvs:
        print 'FAIL', 'no response object'
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

    _test( {"entrez_id": 1956, "end": None, "name": "R776C", "start": None, "referenceName": "GRCh37", "geneSymbol": "EGFR", "alt": "None", "ref": "None", "chromosome": "None"})

    _test({"end": "55242478", "description": "EGFR E746_E749delELRE", "links": ["https://api.molecularmatch.com/v2/mutation/get?name=EGFR+E746_E749delELRE"], "start": "55242467", "biomarker_type": "nonsense", "referenceName": "GRCh37", "alt": "-", "ref": "12", "chromosome": "7", "name": "EGFR E746_E749delELRE"})

    # Testing for AA normalization:

    expected_hgvs_p = "NP_004439.2:p.Ala772_Met775dup"
    expected_hgvs_g = "NC_000017.10:g.37880985_37880996dup"

    civic_entry = {
        "features":[
            {
                "entrez_id":2064,
                "end":37880994,
                "name":"M774INSAYVM",
                "start":37880993,
                "biomarker_type":"Inframe Insertion",
                "referenceName":"GRCh37",
                "geneSymbol":"ERBB2",
                "alt":"GCTTACGTGATG",
                "ref":"None",
                "chromosome":"17",
                "description":"ERBB2 M774INSAYVM"}],
        "civic":{
            "variant_groups":[],
            "entrez_name":"ERBB2",
            "variant_types":[
                {
                    "display_name":"Inframe Insertion",
                    "description":"An inframe non synonymous variant that inserts bases into in the coding sequence.",
                    "url":"http://www.sequenceontology.org/browser/current_svn/term/SO:0001821","so_id":"SO:0001821",
                    "id":106,
                    "name":"inframe_insertion"
                }],
            "description":"Mutations in the HER2 kinase domain occur at a 2-4% frequency in lung adenocarcinomas, the majority of which are in exon 20 as in-frame duplications or insertions in a small 8 codon region (774-781 or 775-782). These are analogous to the exon 20 alterations found in EGFR TK domain. The M774 insertion, M774insAYVM, represents 62.5% of all HER2 kinase domain mutations identified (when combined with the A775insYVMA mutations as they translate to the identical amino acid sequence changes). As demonstrated in mouse models (Perrera et al., PNAS 2009) and subsequent clinical trials in human lung adenocarcinoma with these insertions, HER2 YVMA mutants predict response to several targeted HER2 agonists such as afatinib, trastuzumab, neratinib and TDM-1 (trastuzumab emtansine) as monotherapy or combined with specific chemotherapies.",
            "clinvar_entries":[],
            "lifecycle_actions":{
                "last_modified":{
                    "timestamp":"2017-05-31T22:26:45.259Z",
                    "order":0,
                    "user":{
                        "username":"CIViC_Bot",
                        "area_of_expertise":None,
                        "organization":{},
                        "twitter_handle":"CIViCdb",
                        "name":"CIViC Bot",
                        "bio":None,
                        "url":None,
                        "created_at":"2017-02-20T20:28:47.150Z",
                        "avatars":{
                            "x32":"https://secure.gravatar.com/avatar/e990ea7f667d9e4826a1b3127b324018.png?d=identicon&r=pg&s=32",
                            "x14":"https://secure.gravatar.com/avatar/e990ea7f667d9e4826a1b3127b324018.png?d=identicon&r=pg&s=14",
                            "x64":"https://secure.gravatar.com/avatar/e990ea7f667d9e4826a1b3127b324018.png?d=identicon&r=pg&s=64",
                            "x128":"https://secure.gravatar.com/avatar/e990ea7f667d9e4826a1b3127b324018.png?d=identicon&r=pg&s=128"},
                        "accepted_license":None,
                        "affiliation":None,
                        "avatar_url":"https://secure.gravatar.com/avatar/e990ea7f667d9e4826a1b3127b324018.png?d=identicon&r=pg&s=32",
                        "role":"curator",
                        "facebook_profile":None,
                        "linkedin_profile":None,
                        "orcid":None,
                        "display_name":"CIViC_Bot",
                        "last_seen_at":None,
                        "featured_expert":False,
                        "id":385,
                        "signup_complete":None}},
                "last_reviewed":{
                    "timestamp":"2017-06-01T19:19:22.400Z",
                    "order":1,
                    "user":{
                        "username":"ahwagner",
                        "area_of_expertise":"Research Scientist",
                        "organization":{
                            "url":"http://genome.wustl.edu/",
                            "id":1,
                            "profile_image":{
                                "x32":"/system/organizations/profile_images/000/000/001/x32/MGI_STANDARD4_logo_brown-example_v1b.png?1494525976",
                                "x256":"/system/organizations/profile_images/000/000/001/x256/MGI_STANDARD4_logo_brown-example_v1b.png?1494525976",
                                "x14":"/system/organizations/profile_images/000/000/001/x14/MGI_STANDARD4_logo_brown-example_v1b.png?1494525976",
                                "x64":"/system/organizations/profile_images/000/000/001/x64/MGI_STANDARD4_logo_brown-example_v1b.png?1494525976",
                                "x128":"/system/organizations/profile_images/000/000/001/x128/MGI_STANDARD4_logo_brown-example_v1b.png?1494525976"},
                            "description":"The McDonnell Genome Institute (MGI) is a world leader in the fast-paced, constantly changing field of genomics. A truly unique institution, we are pushing the limits of academic research by creating, testing, and implementing new approaches to the study of biology with the goal of understanding human health and disease, as well as evolution and the biology of other organisms.",
                            "name":"The McDonnell Genome Institute"},
                        "twitter_handle":"HandlerWagner",
                        "name":"Alex Handler Wagner, PhD",
                        "bio":"Dr. Wagner is an NCI Postdoctoral Fellow training at the McDonnell Genome Institute at Washington University School of Medicine. His research interests are focused on the collaborative clinical interpretation of sequence variants in cancers.",
                        "url":"http://alexwagner.info/",
                        "created_at":"2015-02-26T15:58:31.729Z",
                        "avatars":{
                            "x32":"https://secure.gravatar.com/avatar/5a72d8047067d33487a78092f3bbb09e.png?d=identicon&r=pg&s=32",
                            "x14":"https://secure.gravatar.com/avatar/5a72d8047067d33487a78092f3bbb09e.png?d=identicon&r=pg&s=14",
                            "x64":"https://secure.gravatar.com/avatar/5a72d8047067d33487a78092f3bbb09e.png?d=identicon&r=pg&s=64",
                            "x128":"https://secure.gravatar.com/avatar/5a72d8047067d33487a78092f3bbb09e.png?d=identicon&r=pg&s=128"},
                        "accepted_license":None,
                        "affiliation":"",
                        "avatar_url":"https://secure.gravatar.com/avatar/5a72d8047067d33487a78092f3bbb09e.png?d=identicon&r=pg&s=32",
                        "role":"editor",
                        "facebook_profile":"AlexHWagner",
                        "linkedin_profile":"alexphd",
                        "orcid":"0000-0002-2502-8961",
                        "display_name":"ahwagner",
                        "last_seen_at":"2017-06-02T19:45:52.135Z",
                        "featured_expert":False,
                        "id":7,
                        "signup_complete":None}}},
            "provisional_values":{},
            "gene_id":20,
            "evidence_items":[
                {
                    "status":"accepted",
                    "rating":3,
                    "drug_interaction_type":"Combination",
                    "description":"In preclinical studies of transgenic mice and xenografts, continuous expression of mutant ERBB2 (M774insAYVM or the equivalent A775insYVMA) was found to be essential for tumor maintenance. Furthermore, preclinical in vivo studies assessing erlotinib, trastuzumab, afatinib (aka BIBW2992), and/or sirolimus (aka rapamycin) revealed that the combination of afatinib and sirolimus was most effective in shrinking tumors harboring this insertion.",
                    "open_change_count":0,
                    "evidence_type":"Predictive",
                    "drugs":[
                        {"pubchem_id":None,"id":352,"name":"Rapamycin (Sirolimus)"},
                        {"pubchem_id":None,"id":146,"name":"Afatinib"}],
                    "variant_origin":"Somatic Mutation",
                    "disease":{
                        "doid":"3908",
                        "url":"http://www.disease-ontology.org/?id=DOID:3908",
                        "display_name":"Non-small Cell Lung Carcinoma",
                        "id":8,"name":"Non-small Cell Lung Carcinoma"},
                    "source":{
                        "status":"fully curated",
                        "open_access":True,
                        "name":"HER2YVMA drives rapid development of adenosquamous lung tumors in mice that are sensitive to BIBW2992 and rapamycin combination therapy.",
                        "journal":"Proc. Natl. Acad. Sci. U.S.A.",
                        "citation":"Perera et al., 2009, Proc. Natl. Acad. Sci. U.S.A.",
                        "pmc_id":"PMC2626727",
                        "full_journal_title":"Proceedings of the National Academy of Sciences of the United States of America",
                        "source_url":"http://www.ncbi.nlm.nih.gov/pubmed/19122144",
                        "pubmed_id":"19122144",
                        "is_review":False,
                        "publication_date":{
                            "year":2009,"day":13,"month":1},
                        "id":662},
                    "evidence_direction":"Supports",
                    "variant_id":414,
                    "clinical_significance":"Sensitivity",
                    "evidence_level":"D",
                    "type":"evidence",
                    "id":960,
                    "name":"EID960"}],
            "sources":[{
                "status":"fully curated",
                "open_access":True,
                "name":"HER2YVMA drives rapid development of adenosquamous lung tumors in mice that are sensitive to BIBW2992 and rapamycin combination therapy.",
                "journal":"Proc. Natl. Acad. Sci. U.S.A.",
                "citation":"Perera et al., 2009, Proc. Natl. Acad. Sci. U.S.A.",
                "pmc_id":"PMC2626727",
                "full_journal_title":"Proceedings of the National Academy of Sciences of the United States of America",
                "source_url":"http://www.ncbi.nlm.nih.gov/pubmed/19122144",
                "pubmed_id":"19122144",
                "is_review":False,
                "publication_date":{"month":1,"day":13,"year":2009},
                "id":662}],
            "entrez_id":2064,
            "variant_aliases":["P.A775_G776INSYVMA","A775INSYVMA"],
            "hgvs_expressions":["NC_000017.10:g.37880993_37880994insGCTTACGTGATG"],
            "errors":{},
            "coordinates":{
                "chromosome2":None,
                "reference_bases":None,
                "start2":None,
                "variant_bases":"GCTTACGTGATG",
                "stop":37880994,
                "stop2":None,
                "representative_transcript2":None,
                "start":37880993,
                "representative_transcript":"ENST00000269571.5",
                "ensembl_version":75,
                "chromosome":"17",
                "reference_build":"GRCh37"},
            "type":"variant",
            "id":414,
            "name":"M774INSAYVM"},
        "genes":["ERBB2"],
        "source_url":"https://civicdb.org/events/genes/20/summary/variants/414/summary/evidence/960/summary#evidence",
        "source":"civic",
        "feature_names":"EID960",
        "association":{
            "drug_labels":"Rapamycin (Sirolimus),Afatinib","description":"In preclinical studies of transgenic mice and xenografts, continuous expression of mutant ERBB2 (M774insAYVM or the equivalent A775insYVMA) was found to be essential for tumor maintenance. Furthermore, preclinical in vivo studies assessing erlotinib, trastuzumab, afatinib (aka BIBW2992), and/or sirolimus (aka rapamycin) revealed that the combination of afatinib and sirolimus was most effective in shrinking tumors harboring this insertion.",
            "variant_name":"M774INSAYVM",
            "source_link":"https://civic.genome.wustl.edu/events/genes/20/summary/variants/414/summary",
            "publication_url":["http://www.ncbi.nlm.nih.gov/pubmed/19122144"],
            "phenotypes":[{"description":"Non-small Cell Lung Carcinoma","id":"http://www.disease-ontology.org/?id=DOID:3908"}],
            "evidence":[{"info":{"publications":["http://www.ncbi.nlm.nih.gov/pubmed/19122144"]},
                         "evidenceType":{"sourceName":"CIVIC","id":"960"},"description":"Sensitivity"}],
            "environmentalContexts":[
                {"term":"Rapamycin (Sirolimus)","description":"Rapamycin (Sirolimus)","id":None},
                {"term":"Afatinib","description":"Afatinib","id":None}],
            "evidence_label":"D",
            "response_type":"Sensitivity","evidence_level":4}}

    _test(civic_entry, expected_hgvs=expected_hgvs_g)
    _test(civic_entry, expected_hgvs=expected_hgvs_p)

    cgi_entry = {
        "cgi":
             {
                 "Targeting":"",
                 "Source":"AACR 2017 (abstr CT001)","cDNA":[""],
                 "Primary Tumor type":"Any cancer type",
                 "individual_mutation":[""],
                 "Drug full name":"Neratinib (ERBB2 inhibitor)",
                 "Curator":"RDientsmann",
                 "Drug family":"ERBB2 inhibitor",
                 "Alteration":"ERBB2::consequence::inframe_insertion:P780GSP,::inframe_insertion:.781GSP,::inframe_insertion:A775YVMA,::inframe_insertion:G776YVMA",
                 "Drug":"Neratinib",
                 "Biomarker":"ERBB2 inframe insertion (P780GSP),inframe insertion (781GSP),inframe insertion (A775YVMA),inframe insertion (G776YVMA)",
                 "gDNA":[""],
                 "Drug status":"",
                 "Gene":"ERBB2",
                 "transcript":[""],
                 "strand":[""],
                 "info":[""],
                 "Assay type":"",
                 "Alteration type":"MUT",
                 "region":[""],
                 "Evidence level":"Early trials",
                 "Association":"Responsive","Metastatic Tumor Type":""
             },
        "features":[
            {"geneSymbol":"ERBB2","protein_allele":True,"biomarker_type":"ins","description":"Inframe insertion P780GSP","name":"P780GSP"},
            {"geneSymbol":"ERBB2","protein_allele":True,"biomarker_type":"ins","description":"Inframe insertion 781GSP","name":"781GSP"},
            {"geneSymbol":"ERBB2","protein_allele":True,"biomarker_type":"ins","description":"Inframe insertion A775YVMA","name":"A775YVMA"},
            {"geneSymbol":"ERBB2","protein_allele":True,"biomarker_type":"ins","description":"Inframe insertion G776YVMA","name":"G776YVMA"}
        ],
        "genes":["ERBB2"],
        "source_url":"https://www.cancergenomeinterpreter.org/biomarkers",
        "source":"cgi",
        "feature_names":"ERBB2 inframe insertion (P780GSP),inframe insertion (781GSP),inframe insertion (A775YVMA),inframe insertion (G776YVMA)",
        "association":{
            "drug_labels":"Neratinib (ERBB2 inhibitor)",
            "description":"ERBB2 Neratinib (ERBB2 inhibitor) Responsive",
            "publication_url":"https://www.google.com/#q=AACR 2017 (abstr CT001)",
            "phenotypes":[{"description":"Any cancer type"}],
            "evidence":[
                {
                    "info":{"publications":["https://www.google.com/#q=AACR 2017 (abstr CT001)"]},
                    "evidenceType":{"sourceName":"cgi"},"description":"Responsive"}
            ],
            "environmentalContexts":[{"description":"Neratinib (ERBB2 inhibitor)"}],
            "evidence_label":"C",
            "response_type":"Responsive",
            "evidence_level":3
        }
    }

    _test(cgi_entry, expected_hgvs=expected_hgvs_g)
    _test(cgi_entry, expected_hgvs=expected_hgvs_p)

    jax_entry = {
        "features":[{"geneSymbol":"ERBB2","name":"ERBB2 Y772_A775dup "}],
        "jax":{
            "responseType":"no benefit",
            "efficacyEvidence":"In a retrospective study, Vizimpro (dacomitinib) treatment resulted in an objective response rate of 0% (0/13) in non-small cell lung cancer patients harboring ERBB2 (HER2) Y772_A775dup (reported as (A775_G776insYVMA) (PMID: 30527195).",
            "molecularProfile":{"profileName":"ERBB2 Y772_A775dup","id":3148},
            "evidenceType":"Actionable",
            "therapy":{"id":714,"therapyName":"Dacomitinib"},
            "references":[{
                "url":"http://www.ncbi.nlm.nih.gov/pubmed/30527195",
                "id":13464,
                "pubMedId":30527195,
                "title":"Activity of a novel HER2 inhibitor, poziotinib, for HER2 exon 20 mutations in lung cancer and mechanism of acquired resistance: An in vitro study."}],
            "approvalStatus":"Clinical Study",
            "indication":{"source":"DOID","id":3908,"name":"non-small cell lung carcinoma"},
            "id":15598},
        "genes":["ERBB2"],
        "source_url":"https://ckb.jax.org/therapy/show/714",
        "source":"jax",
        "feature_names":"ERBB2 Y772_A775dup",
        "association":{
            "drug_labels":"Dacomitinib",
            "description":"In a retrospective study, Vizimpro (dacomitinib) treatment resulted in an objective response rate of 0% (0/13) in non-small cell lung cancer patients harboring ERBB2 (HER2) Y772_A775dup (reported as (A775_G776insYVMA) (PMID: 30527195).",
            "variant_name":["Y772_A775dup"],
            "source_link":"https://ckb.jax.org/molecularProfile/show/3148",
            "publication_url":"http://www.ncbi.nlm.nih.gov/pubmed/30527195",
            "phenotypes":[{"description":"non-small cell lung carcinoma","id":"DOID:3908"}],
            "evidence":[{"info":{"publications":["http://www.ncbi.nlm.nih.gov/pubmed/30527195"]},
                         "evidenceType":{"sourceName":"jax"},"description":"no benefit"}],
            "environmentalContexts":[{"description":"Dacomitinib"}],
            "evidence_label":"C",
            "response_type":"no benefit",
            "evidence_level":3}
    }

    _test(jax_entry, expected_hgvs=expected_hgvs_g)
    _test(jax_entry, expected_hgvs=expected_hgvs_p)

    mm_entry = {"molecularmatch":{
        "criteriaUnmet":[
            {
                "priority":0,
                "term":"Neoplasm of lung",
                "suppress":False,
                "generatedBy":"CONDITION",
                "filterType":"include",
                "custom":False,
                "facet":"CONDITION",
                "generatedByTerm":"Malignant tumor of lung"},
            {
                "priority":1,
                "compositeKey":"ERBB2 A775_G776insYVMAMUTATIONinclude",
                "suppress":False,
                "filterType":"include",
                "term":"ERBB2 A775_G776insYVMA",
                "custom":True,
                "facet":"MUTATION",
                "valid":True}],
        "prevalence":[
            {"count":0,"percent":0,"samples":0,"studyId":"PAN CANCER MAX"},
            {"count":0,"percent":0,"samples":0,"studyId":"PAN CANCER AVG"}],
        "_score":3,
        "autoGenerateNarrative":True,
        "mutations":[
            {"transcriptConsequence":[
                {
                    "amino_acid_change":"p.Y772_A775dupYVMA",
                     "compositeKey":"3e6c6a9850e421b89026dacc30634aa1",
                     "intronNumber":None,
                     "ref":"-",
                     "exonNumber":"20",
                     "suppress":False,
                     "stop":"37880997",
                     "custom":False,
                     "start":"37880996",
                     "chr":"17",
                     "strand":"+",
                     "alt":"TATGTAATGGCA",
                     "validated":"transvar",
                     "transcript":"CCDS32642",
                     "cdna":"c.2325_2326insTATGTAATGGCA",
                     "referenceGenome":"grch37_hg19"
                },
                {
                    "amino_acid_change":"p.Y772_A775dupYVMA",
                    "compositeKey":"b179240e797bf1890b584b126127c946",
                    "intronNumber":None,
                    "ref":"-",
                    "exonNumber":"20",
                    "suppress":False,
                    "stop":"37880997",
                    "custom":False,
                    "start":"37880996",
                    "chr":"17",
                    "strand":"+",
                    "alt":"TATGTAATGGCA",
                    "validated":"transvar",
                    "transcript":"ENST00000269571",
                    "cdna":"c.2325_2326insTATGTAATGGCA",
                    "referenceGenome":"grch37_hg19"},
                {
                    "amino_acid_change":"p.Y772_A775dupYVMA",
                    "compositeKey":"23684b4f566eb9bdf63940585e398569",
                    "intronNumber":None,
                    "ref":"-",
                    "exonNumber":"20",
                    "suppress":False,
                    "stop":"37880997",
                    "custom":False,
                    "start":"37880996",
                    "chr":"17",
                    "strand":"+",
                    "alt":"TATGTAATGGCA",
                    "validated":"transvar",
                    "transcript":"ENST00000584450",
                    "cdna":"c.2325_2326insTATGTAATGGCA",
                    "referenceGenome":"grch37_hg19"},
                {
                    "amino_acid_change":"p.Y772_A775dupYVMA",
                    "compositeKey":"6bc5fa2c20006805309d202c9f500c52",
                    "intronNumber":None,
                    "ref":"-",
                    "exonNumber":"20",
                    "suppress":False,
                    "stop":"37880997",
                    "custom":False,
                    "start":"37880996",
                    "chr":"17",
                    "strand":"+",
                    "alt":"TATGTAATGGCA",
                    "validated":"transvar",
                    "transcript":"NM_001289937",
                    "cdna":"c.2325_2326insTATGTAATGGCA",
                    "referenceGenome":"grch37_hg19"},
                {
                    "amino_acid_change":"p.Y772_A775dupYVMA",
                    "compositeKey":"33effb6da373a76a5e1db58c073e37cd",
                    "intronNumber":None,
                    "ref":"-",
                    "exonNumber":"20",
                    "suppress":False,
                    "stop":"37880997",
                    "custom":False,
                    "start":"37880996",
                    "chr":"17",
                    "strand":"+",
                    "alt":"TATGTAATGGCA",
                    "validated":"transvar",
                    "transcript":"NM_004448",
                    "cdna":"c.2325_2326insTATGTAATGGCA",
                    "referenceGenome":"grch37_hg19"},
                {
                    "amino_acid_change":"A775_G776insYVMA",
                    "compositeKey":"543e01feb26f2a32c0fc090f90a72dce",
                    "intronNumber":None,
                    "ref":"-",
                    "exonNumber":"20",
                    "suppress":False,
                    "stop":"37880981",
                    "custom":False,
                    "start":"37880981",
                    "chr":"17",
                    "strand":"+",
                    "alt":"GCATACGTGATG",
                    "validated":"wgsa",
                    "transcript":"NM_004448.3",
                    "cdna":"c.2223_2234dupATACGTGATGGC",
                    "referenceGenome":"grch37_hg19"},
                {
                    "amino_acid_change":"A775_G776insYVMA",
                    "compositeKey":"38d516298b929b0429c998447bd46fce",
                    "intronNumber":None,
                    "ref":"-",
                    "exonNumber":"20",
                    "suppress":False,
                    "stop":"37880995",
                    "custom":False,
                    "start":"37880995",
                    "chr":"17",
                    "strand":"+",
                    "alt":"ATACGTGATGGC",
                    "validated":"wgsa",
                    "transcript":"NM_004448.3",
                    "cdna":"c.2223_2234dupATACGTGATGGC",
                    "referenceGenome":"grch37_hg19"}],
                "longestTranscript":"NM_004448.3",
                "description":"",
                "mutation_type":["In Frame","Insertion"],
                "_src":1,
                "sources":["COSMIC"],
                "synonyms":[],
                "parents":[{"transcripts":[],"type":None,"name":"HER2 Mutations"}],
                "GRCh37_location":[
                    {
                        "compositeKey":"bc87c07ca5150747fbb795ba979580bc",
                        "ref":"-",
                        "stop":"37880997",
                        "start":"37880996",
                        "chr":"17",
                        "alt":"TATGTAATGGCA",
                        "validated":"transvar",
                        "transcript_consequences":[
                            {
                                "amino_acid_change":"p.Y772_A775dupYVMA",
                                "txSites":[],
                                "exonNumber":"20",
                                "intronNumber":None,
                                "transcript":"CCDS32642",
                                "cdna":"c.2325_2326insTATGTAATGGCA"},
                            {
                                "amino_acid_change":"p.Y772_A775dupYVMA",
                                "txSites":[],
                                "exonNumber":"20",
                                "intronNumber":None,
                                "transcript":"ENST00000269571",
                                "cdna":"c.2325_2326insTATGTAATGGCA"},
                            {
                                "amino_acid_change":"p.Y772_A775dupYVMA",
                                "txSites":[],
                                "exonNumber":"20",
                                "intronNumber":None,
                                "transcript":"ENST00000584450",
                                "cdna":"c.2325_2326insTATGTAATGGCA"},
                            {"amino_acid_change":"p.Y772_A775dupYVMA",
                             "txSites":[],
                             "exonNumber":"20",
                             "intronNumber":None,
                             "transcript":"NM_001289937",
                             "cdna":"c.2325_2326insTATGTAATGGCA"},
                            {
                                "amino_acid_change":"p.Y772_A775dupYVMA",
                                "txSites":[],
                                "exonNumber":"20",
                                "intronNumber":None,
                                "transcript":"NM_004448",
                                "cdna":"c.2325_2326insTATGTAATGGCA"}],
                        "strand":"+"},
                    {
                        "compositeKey":"90121667121eedae8c8c9386316d2490",
                        "ref":"-","stop":"37880981",
                        "start":"37880981",
                        "chr":"17",
                        "alt":"GCATACGTGATG",
                        "validated":"wgsa",
                        "transcript_consequences":[
                            {
                                "amino_acid_change":"A775_G776insYVMA",
                                "txSites":[],
                                "exonNumber":"20",
                                "intronNumber":None,
                                "transcript":"NM_004448.3",
                                "cdna":"c.2223_2234dupATACGTGATGGC"}],
                        "strand":"+"},
                    {
                        "compositeKey":"4045756f598df2f0bb73f787c72db511",
                        "ref":"-",
                        "stop":"37880995",
                        "start":"37880995",
                        "chr":"17","alt":"ATACGTGATGGC",
                        "validated":"wgsa",
                        "transcript_consequences":[
                            {
                                "amino_acid_change":"A775_G776insYVMA",
                                "txSites":[],
                                "exonNumber":"20",
                                "intronNumber":None,
                                "transcript":"NM_004448.3",
                                "cdna":"c.2223_2234dupATACGTGATGGC"}],
                        "strand":"+"}],
                "uniprotTranscript":"NM_004448.3",
                "geneSymbol":"ERBB2",
                "pathology":[],
                "transcript":"NM_004448.3",
                "id":"e94992f923d4e81a02e4cc5951626655",
                "cdna":["c.2325_2326ins12","c.2324_2325ins12"],
                "name":"ERBB2 A775_G776insYVMA"}],
        "sources":[
            {
                "name":"PUBMED",
                "suppress":False,
                "pubId":"26545934",
                "subType":"cell_line",
                "valid":True,
                "link":"https://www.ncbi.nlm.nih.gov/pubmed/26545934",
                "year":"",
                "type":"preclinical",
                "id":"1"},
            {
                "name":"PUBMED",
                "suppress":False,
                "pubId":"26559459",
                "valid":True,
                "link":"https://www.ncbi.nlm.nih.gov/pubmed/26559459",
                "year":"",
                "type":"case_study",
                "id":"2"},
            {
                "name":"PUBMED",
                "suppress":False,
                "pubId":"22325357",
                "valid":True,
                "link":"https://www.ncbi.nlm.nih.gov/pubmed/22325357",
                "year":"",
                "type":"case_study",
                "id":"3"}],
        "clinicalSignificance":"sensitive",
        "id":"259ee9a8-7b25-4e81-b1ac-a47adaa64532",
        "includeCondition0":[
            "Neoplasm by body site",
            "Disorder of respiratory system",
            "Disorder of body system",
            "Disease",
            "Disorder of thoracic segment of trunk",
            "Neoplastic disease",
            "Disorder by body site",
            "Neoplasm of lung",
            "Disorder of trunk",
            "Malignant neoplasm of lower respiratory tract",
            "Malignant neoplasm of respiratory system",
            "Disorder of thorax",
            "Neoplasm of respiratory tract",
            "Neoplasm of respiratory system",
            "Neoplasm of lower respiratory tract",
            "Malignant neoplastic disease",
            "Disorder of lung",
            "Disorder of lower respiratory system",
            "Malignant neoplasm of thorax",
            "Neoplasm of intrathoracic organs",
            "Neoplasm and/or hamartoma",
            "Neoplasm of thorax",
            "Neoplasm of trunk",
            "Solid tumor"],
        "includeCondition1":["Malignant tumor of lung"],
        "uniqueKey":"ed2ec0a16a00ad630d3eae6e78a5b213",
        "civic":"A",
        "hashKey":"90a93f0a6ca1177337d5e8b2e2544d4e",
        "regulatoryBodyApproved":True,
        "version":2,
        "includeMutation1":["ERBB2 A775_G776insYVMA"],
        "includeMutation0":["HER2 Mutations","ERBB2 Gain of Function"],
        "regulatoryBody":"FDA",
        "customer":"MolecularMatch",
        "direction":"supports",
        "ampcap":"1A",
        "ast":{
            "operator":"&&",
            "right":{"raw":"\"ERBB2 A775_G776insYVMA\"","type":"Literal","value":"ERBB2 A775_G776insYVMA"},
            "type":"LogicalExpression",
            "left":{"raw":"\"Neoplasm of lung\"","type":"Literal","value":"Neoplasm of lung"}},
        "variantInfo":[
            {
                "classification":"actionable",
                "name":"ERBB2 A775_G776insYVMA",
                "consequences":["In Frame","Insertion"],
                "fusions":[],
                "locations":[
                    {
                        "amino_acid_change":"Y772_A775dupYVMA",
                        "intronNumber":"",
                        "exonNumber":"20",
                        "stop":"37880997",
                        "start":"37880996",
                        "chr":"17",
                        "strand":"+",
                        "alt":"TATGTAATGGCA",
                        "referenceGenome":"grch37_hg19",
                        "ref":"-",
                        "cdna":"c.2325_2326insTATGTAATGGCA"}],
                "geneFusionPartner":"",
                "COSMIC_ID":"COSM5350378",
                "gene":"ERBB2",
                "transcript":"NM_004448.3",
                "popFreqMax":"0"}],
        "tier":"1A",
        "tierExplanation":[
            {
                "tier":"1A",
                "step":1,
                "message":"FDA Approved",
                "success":True}],
        "mvld":"1","tags":[
            {
                "priority":1,
                "compositeKey":"Malignant tumor of lungCONDITIONinclude",
                "suppress":False,
                "filterType":"include",
                "term":"Malignant tumor of lung",
                "primary":True,
                "facet":"CONDITION",
                "valid":True,"custom":True},
            {
                "priority":1,
                "compositeKey":"ERBB2 A775_G776insYVMAMUTATIONinclude",
                "suppress":False,
                "filterType":"include",
                "term":"ERBB2 A775_G776insYVMA",
                "custom":True,
                "facet":"MUTATION",
                "valid":True},
            {
                "priority":0,"term":"ERBB2",
                 "suppress":False,
                 "generatedBy":"MUTATION",
                 "filterType":"include",
                 "custom":False,
                "facet":"GENE",
                "generatedByTerm":"ERBB2 A775_G776insYVMA"},
            {
                "priority":0,
                "term":"HER2 Mutations",
                "suppress":False,
                "generatedBy":"MUTATION",
                "filterType":"include",
                "custom":False,
                "facet":"MUTATION",
                "generatedByTerm":"ERBB2 A775_G776insYVMA"},
            {
                "priority":0,
                "term":"ERBB2 Gain of Function",
                "suppress":False,
                "generatedBy":"MUTATION",
                "filterType":"include",
                "custom":False,
                "facet":"MUTATION",
                "generatedByTerm":"ERBB2 A775_G776insYVMA"},
            {
                "priority":0,
                "term":"Lung structure",
                "suppress":False,
                "generatedBy":"CONDITION",
                "filterType":"include",
                "custom":False,
                "facet":"SITE",
                "generatedByTerm":"Malignant tumor of lung"},
            {"priority":0,
             "term":"Neoplasm by body site",
             "suppress":False,
             "generatedBy":"CONDITION",
             "filterType":"include",
             "custom":False,
             "facet":"CONDITION",
             "generatedByTerm":"Malignant tumor of lung"},
            {
                "priority":0,
                "term":"Disorder of respiratory system",
                "suppress":False,
                "generatedBy":"CONDITION",
                "filterType": "include", "custom": False, "facet": "CONDITION",
                "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disorder of body system", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disease", "suppress": False, "generatedBy": "CONDITION", "filterType": "include",
             "custom": False, "facet": "CONDITION", "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disorder of thoracic segment of trunk", "suppress": False,
             "generatedBy": "CONDITION", "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplastic disease", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disorder by body site", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm of lung", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disorder of trunk", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Malignant neoplasm of lower respiratory tract", "suppress": False,
             "generatedBy": "CONDITION", "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Malignant neoplasm of respiratory system", "suppress": False,
             "generatedBy": "CONDITION", "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disorder of thorax", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm of respiratory tract", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm of respiratory system", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm of lower respiratory tract", "suppress": False,
             "generatedBy": "CONDITION", "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Malignant neoplastic disease", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disorder of lung", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Disorder of lower respiratory system", "suppress": False,
             "generatedBy": "CONDITION", "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Malignant neoplasm of thorax", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm of intrathoracic organs", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm and/or hamartoma", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm of thorax", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Neoplasm of trunk", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"},
            {"priority": 0, "term": "Solid tumor", "suppress": False, "generatedBy": "CONDITION",
             "filterType": "include", "custom": False, "facet": "CONDITION",
             "generatedByTerm": "Malignant tumor of lung"}], "criteriaMet": [], "biomarkerClass": "predictive",
        "classifications": [
            {"End": ["37880981", "37880995"], "classification": "actionable", "classificationOverride": None,
             "Start": ["37880981", "37880995"], "Chr": ["17"], "geneSymbol": "ERBB2", "pathology": [], "Ref": ["-"],
             "description": "", "priority": 1, "NucleotideChange": ["c.2313_2324dupATACGTGATGGC"],
             "parents": [{"transcripts": [], "type": None, "name": "HER2 Mutations"}], "drugsExperimentalCount": 0,
             "Exon": ["20"], "drugsApprovedOffLabelCount": 0, "ExonicFunc": ["in-frame"], "PopFreqMax": [0],
             "copyNumberType": None, "publicationCount": 2, "transcript": None, "dbSNP": ["rs397516975;rs397516976"],
             "Alt": ["GCATACGTGATG", "ATACGTGATGGC"], "name": "ERBB2 A775_G776insYVMA",
             "rootTerm": "ERBB2 A775_G776insYVMA", "sources": ["COSMIC"], "drugsApprovedOnLabelCount": 1,
             "trialCount": 9, "alias": "ERBB2 A775_G776insYVMA", "COSMIC_ID": ["COSM5350378", "COSM20959"],
             "transcripts": []}], "includeDrug1": ["Afatinib"],
        "therapeuticContext": [{"facet": "DRUG", "suppress": False, "valid": True, "name": "Afatinib"}], "sixtier": "1",
        "narrative": "ERBB2 A775_G776insYVMA confers sensitivity to Afatinib in patients with Neoplasm of lung",
        "expression": "\"Neoplasm of lung\" && \"ERBB2 A775_G776insYVMA\"", "includeGene0": ["ERBB2"]}, "features": [
        {"protein_allele": True, "end": 37880997, "description": "ERBB2 A775_G776insYVMA", "start": 37880996,
         "biomarker_type": "ins", "referenceName": "GRCh37", "geneSymbol": "ERBB2", "alt": "TATGTAATGGCA", "ref": "-",
         "chromosome": "17", "name": "A775_G776insYVMA"}], "genes": ["ERBB2"], "source": "molecularmatch",
        "feature_names": "ERBB2 A775_G776insYVMA", "association": {
           "drug_labels": "Afatinib",
           "description": "ERBB2 A775_G776insYVMA confers sensitivity to Afatinib in patients with Neoplasm of lung",
           "variant_name": ["Y772_A775dupYVMA"],
           "publication_url": "https://www.ncbi.nlm.nih.gov/pubmed/26545934",
           "phenotypes": [
               {"description": "Malignant tumor of lung"},
               {"description": "Neoplasm by body site"}, {
                   "description": "Disorder of respiratory system"},
               {"description": "Disorder of body system"},
               {"description": "Disease"}, {
                   "description": "Disorder of thoracic segment of trunk"},
               {"description": "Neoplastic disease"},
               {"description": "Disorder by body site"},
               {"description": "Neoplasm of lung"},
               {"description": "Disorder of trunk"}, {
                   "description": "Malignant neoplasm of lower respiratory tract"},
               {
                   "description": "Malignant neoplasm of respiratory system"},
               {"description": "Disorder of thorax"},
               {"description": "Neoplasm of respiratory tract"},
               {
                   "description": "Neoplasm of respiratory system"},
               {
                   "description": "Neoplasm of lower respiratory tract"},
               {"description": "Malignant neoplastic disease"},
               {"description": "Disorder of lung"}, {
                   "description": "Disorder of lower respiratory system"},
               {"description": "Malignant neoplasm of thorax"},
               {
                   "description": "Neoplasm of intrathoracic organs"},
               {"description": "Neoplasm and/or hamartoma"},
               {"description": "Neoplasm of thorax"},
               {"description": "Neoplasm of trunk"},
               {"description": "Solid tumor"}], "evidence": [{
                     "info": {
                         "publications": [
                             "https://www.ncbi.nlm.nih.gov/pubmed/26545934",
                             "https://www.ncbi.nlm.nih.gov/pubmed/26559459",
                             "https://www.ncbi.nlm.nih.gov/pubmed/22325357"]},
                     "evidenceType": {
                         "sourceName": "molecularmatch"},
                     "description": "ERBB2 A775_G776insYVMA confers sensitivity to Afatinib in patients with Neoplasm of lung"}],
           "environmentalContexts": [
               {"description": "Afatinib"}],
           "evidence_label": "A", "response_type": "1A",
           "evidence_level": 1}}

    _test(mm_entry, expected_hgvs=expected_hgvs_g)
    _test(mm_entry, expected_hgvs=expected_hgvs_p)
