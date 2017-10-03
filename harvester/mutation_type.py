

def norm_biomarker(evidence, cgi_biomarker=None):
    """ Map alteration type to standardized biomarker type. """
    if evidence:
        ev = evidence.lower()
    else:
        return 'NA'

    # Note that 'CNA' is currently left out as it is relevant only in the case
    # of CGI and directed in for loop below. 
    mut_types = {
        'biallelic inactivation' : ['bia'],
        'decreased expression' : ['dec exp'],
        'deletion' : ['deletion'],
        'exon' : ['exon'], # civic
        'frameshift' : ['frameshift'],
        'fusion' : ['fusion', 'fus'],
        'gain of function' : ['gain of function'], # civic
        'indel' : ['indel'],
        'insertion' : ['insertion'],
        'intron' : ['intron variant'],
        'loss of function' : ['loss of function'], # civic
        'loss of heterozygosity' : ['loss of heterozygosity'], # civic
        'overexpression' : ['expr', 'over exp'],
        'silent' : ['silent mutation', 'synonymous', 'inact mut'],
        'snp' : ['snp', 'mut', 'mutant', 'missense', 'protein altering', 'coding sequence', 'nonsense'],
        'startloss' : ['start lost'],
	'stopgain' : ['stop gained'],
        'transcript': ['transcript'], # civic
        'unspecified' : ['na', 'n/a', 'gene variant', 'any'], # civic
        'wild-type' : ['wild-type', 'wild type']
        '3 Prime UTR' : ['3 prime utr'],
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
