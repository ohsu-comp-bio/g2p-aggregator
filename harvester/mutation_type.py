# DEPRECATED

def norm_biomarker(evidence, cgi_biomarker=None):
    """ Map alteration type to standardized biomarker type. """
    if evidence:
        ev = evidence.lower()
    else:
        return 'NA'

    # Note that 'CNA' is currently left out as it is relevant only in the case
    # of CGI and directed in for loop below.

    #  BRCA Exchange
    # F(Frameshift),
    # 3'UTR(3'UTR 3-prime Untranslated Region),
    # 5'UTR(5'UTR 5-prime Untranslated Region),
    # IFI(In Frame Insertion),
    # IFD(In Frame Deletion),
    # IVS(Intervening Sequence),
    # M(Missense),
    # N(Nonsense),
    # P(Polymorphism),
    # S(Splice),
    # Syn(Synonymous),
    # UV(Unclassified Variant)

    mut_types = {
        "3'UTR": ["3'utr"],  # 3-prime Untranslated Region
        "5'UTR": ["5'utr"],  # 5-prime Untranslated Region
        'amplification': ['amp'],  # gene is amplified
        'biallelic inactivation': ['bia'],
        # gene or protein has decreased expression
        'decreased expression': ['dec exp'],
        'deletion': ['deletion', 'del', 'ifd'],  # gene  is deleted
        'exon': ['exon'],  # civic
        'frameshift': ['frameshift', 'f'],
        'fusion': ['fusion', 'fus'],  # gene fusion
        # gain of protein function
        'gain of function': ['gain of function', 'act mut'],
        'indel': ['indel'],
        'intervening sequence': ['ivs'],  # IVS(Intervening Sequence),
        'insertion': ['insertion', 'ifi'],
        'intron': ['intron variant'],
        'loss': ['loss'],  # gene or protein is lost
        # loss of protein function
        'loss of function': ['loss of function', 'inact mut'],
        'loss of heterozygosity': ['loss of heterozygosity'],  # civic
        'missense': ['m'],
        # unspecified mutation
        'mutant': ['mutant', 'mut', 'na', 'n/a', 'gene variant', 'any',
                   '-', 'uv'],
        'negative': ['negative', 'neg'],  # lack of gene or protein
        'nonsense': ['n'],
        # gene or protein has increased expression
        'over expression': ['expr', 'over exp'],
        'positive': ['positive', 'pos'],  # gene or protein is present
        'polymorphism': ['p'],

        'rearrangement': ['rearrange'],  # unspecified gene rearrangement
        'silent': ['silent mutation', 'synonymous'],
        'snp': ['snp', 'missense', 'protein altering', 'coding sequence',
                'nonsense'],
        'splice': ['s'],
        'synonymous': ['syn'],
        'startloss': ['start lost'],
        'stopgain': ['stop gained'],
        'transcript': ['transcript'],  # civic
        'wild-type': ['wild-type', 'wild type'],  # no mut. detected in gene
        '3 Prime UTR': ['3 prime utr'],
        'copy number variant': ['copy number variant']
    }

    for mut in mut_types:
        for opt in mut_types[mut]:
            if opt in ev:
                return mut
            elif ev == "cna":
                # Copy number alteration, either amplification or deletion.
                # This is only relevant in the case of CGI
                if "amplification" in cgi_biomarker:
                    return "amplification"
                elif "deletion" in cgi_biomarker:
                    return "deletion"
    return ev
