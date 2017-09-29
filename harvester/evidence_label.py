
# normalized vocabulary for evidence_label
# 'FDA guidelines', 'preclinical', 'trials', 'NCCN guidelines',  or
# 'European LeukemiaNet Guidelines'

# see https://docs.google.com/spreadsheets/d/1j9AKdv1k87iO8qH-ujnW3x4VusbGoXDjdb5apUqJsSI/edit#gid=1415903760


def evidence_label(evidence=None, association, na=False):
    # CGI
    # Drug status?? VICC group??
    # cgi_a = ['clinical practice']
    # cgi_b = ['clinical trials iii', 'clinical trials iv']
    # cgi_c = ['clinical trials i', 'clinical trials ii', 'case reports']
    # cgi_d = ['pre-clinical data']

    # CGI
    # Evidence level
    cgi_a = ['cpic guidelines', 'european leukemianet guidelines', 'fda guidelines', 'nccn guidelines', 'nccn/cap guidelines']  # NOQA
    cgi_b = ['late trials', 'late trials,pre-clinical']
    cgi_c = ['early trials', 'case report', 'clinical trial',
             'early trials,case report']
    cgi_d = ['pre-clinical']




    # JAX
    jax_a = ['guideline', 'fda approved']
    jax_b = ['phase iii']
    jax_c = ['phase i', 'phase ib', 'phase ib/ii', 'phase ii', 'clinical study']
    jax_d = ['phase 0', 'preclinical', 'preclinical - cell line xenograft', 'preclinical - cell culture', 'preclinical - pdx', 'preclinical - patient cell culture', 'preclinical - pdx & cell culture'] # NOQA

    # PMKB
    pmkb_a = ['1']
    pmkb_b = []
    pmkb_c = ['2']
    pmkb_d = ['3']

    # CIVIC
    civic_a = ['a']
    civic_b = ['b']
    civic_c = ['c']
    civic_d = ['d', 'e']

    # ONCOKB
    oncokb_a = ['1', 'r1']
    oncokb_b = ['2a']
    oncokb_c = ['2b', '3a', '3b']
    oncokb_d = ['4']

    # molecularmatch
    molecularmatch_a = ['1', '1a', '1b']
    molecularmatch_b = ['2', '2c', '2d']
    molecularmatch_c = ['3']
    molecularmatch_d = ['4', '5']

    ev_lab = {
        'A': cgi_a + jax_a + pmkb_a + civic_a + oncokb_a + molecularmatch_a,
        'B': cgi_b + jax_b + pmkb_b + civic_b + oncokb_b + molecularmatch_b,
        'C': cgi_c + jax_c + pmkb_c + civic_c + oncokb_c + molecularmatch_c,
        'D': cgi_d + jax_d + pmkb_d + civic_d + oncokb_d + molecularmatch_d
    }

    ev_lev = {
        'A' : 1,
        'B' : 2,
        'C' : 3,
        'D' : 4
    }

    for item in ev_lab:
        for opt in ev_lab[item]:
            if evidence and opt == evidence.lower():
                association['evidence_label'] = item
                association['evidence_level'] = ev_lev[item]
    if 'evidence_label' not in association:
        if na:
            association['evidence_label'] = 'NA'
            # association['evidence_level'] = 'NA'
        else:
            association['evidence_label'] = evidence
            # association['evidence_level'] = evidence
    return association
