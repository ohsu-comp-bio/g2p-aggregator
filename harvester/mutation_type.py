

def norm_biomarker(evidence, cgi_biomarker=None):
    """ Map alteration type to standardized biomarker type. """
    if evidence:
        ev = evidence.lower()
    else:
        return 'NA'

    # Note that 'CNA' is currently left out as it is relevant only in the case
    # of CGI and directed in for loop below. 
    mut_types = {
        'amplification' : ['amp'], # gene is amplified
        'biallelic inactivation' : ['bia'],
        'decreased expression' : ['dec exp'], # gene or protein has decreased expression
        'deletion' : ['deletion', 'del'], # gene  is deleted
        'exon' : ['exon'], # civic
        'frameshift' : ['frameshift'],
        'fusion' : ['fusion', 'fus'], # gene fusion
        'gain of function' : ['gain of function', 'act mut'], # gain of protein function
        'indel' : ['indel'],
        'insertion' : ['insertion'],
        'intron' : ['intron variant'],
        'loss' : ['loss'], # gene or protein is lost
        'loss of function' : ['loss of function', 'inact mut'], # loss of protein function
        'loss of heterozygosity' : ['loss of heterozygosity'], # civic
        'mutant': ['mutant', 'mut', 'na', 'n/a', 'gene variant', 'any'], # unspecified mutation
        'negative': ['negative', 'neg'], # lack of gene or protein
        'over expression' : ['expr', 'over exp'], # gene or protein has increased expression
        'positive': ['positive', 'pos'], # gene or protein is present
        'rearrangement': ['rearrange'], # unspecified gene rearrangement
        'silent' : ['silent mutation', 'synonymous'],
        'snp' : ['snp', 'missense', 'protein altering', 'coding sequence', 'nonsense'],
        'startloss' : ['start lost'],
	'stopgain' : ['stop gained'],
        'transcript': ['transcript'], # civic
        'wild-type' : ['wild-type', 'wild type'], # no mutation detected in gene
        '3 Prime UTR' : ['3 prime utr']
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
