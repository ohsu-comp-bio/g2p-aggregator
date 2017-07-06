

def norm_biomarker(evidence, cgi_biomarker=None):
    """ Map alteration type to standardized biomarker type. """
    if evidence:
        ev = evidence.lower()
    else:
        return 'NA'

    # Note that 'CNA' is currently left out as it is relevant only in the case
    # of CGI and directed in for loop below. 
    mut_types = {
        'fusion' : ['fusion', 'fus'],
        'snp' : ['snp', 'mut', 'missense', 'protein altering', 'coding sequence', 'nonsense'],
        'biallelic inactivation' : ['bia'],
        'overexpression' : ['expr'],
        'unspecified' : ['na', 'n/a', 'gene variant', 'wild type', 'any'], # civic
        'exon' : ['exon'], # civic
        'transcript': ['transcript'], # civic
        'loss of function' : ['loss of function'], # civic
        'gain of function' : ['gain of function'], # civic
        'frameshift' : ['frameshift'],
        'loss of heterozygosity' : ['loss of heterozygosity'], # civic
        'deletion' : ['deletion'],
        'insertion' : ['insertion'],
        '3 Prime UTR' : ['3 prime utr'],
        'stopgain' : ['stop gained'],
        'startloss' : ['start lost'],
        'silent' : ['silent mutation', 'synonymous'],
        'intron' : ['intron variant'],
        'indel' : ['indel']
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
