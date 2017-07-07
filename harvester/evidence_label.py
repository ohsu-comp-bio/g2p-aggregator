
# normalized vocabulary for evidence_label
# 'FDA guidelines', 'preclinical', 'trials', 'NCCN guidelines',  or
# 'European LeukemiaNet Guidelines'

# see https://docs.google.com/spreadsheets/d/1j9AKdv1k87iO8qH-ujnW3x4VusbGoXDjdb5apUqJsSI/edit#gid=1415903760


def evidence_label(evidence, association, na=False):
    fda = ['fda guidelines', 'fda-approved', 'fda approved', '1', 'guideline']
    nccn = ['nccn guidelines', 'nccn-approved', 'nccn approved',
            'nccn/cap guidelines']
    eln = ['european leukemianet guidelines']
    preclinical = ['preclinical', 'pre-clinical', '3']
    trials_c = ['early trials', 'late trials', 'phase 2', '2',
                'phase ii', 'phase 1', 'phase i', 'clinical trial',
                'clinical study']
    trials_b = ['phase 3', 'phase iii']
    civic_a = ['a']
    civic_b = ['b']
    civic_c = ['c']
    civic_d = ['d', 'e']

    cr = ['case report']
    oncokb_b = ['compelling clinical evidence supports the biomarker as being predictive of response to a drug in this indication but neither biomarker and drug are standard of care']  # NOQA
    oncokb_c = ['compelling biological evidence supports the biomarker as being predictive of response to a drug but neither biomarker and drug are standard of care']  # NOQA

    ev_lab = {
        'A': fda + nccn + eln + civic_a,
        'B': trials_b + oncokb_b + civic_b,
        'C': trials_c + oncokb_c + civic_c,
        'D': cr + preclinical + civic_d
    }

    for item in ev_lab:
        for opt in ev_lab[item]:
            if evidence and opt in evidence.lower():
                association['evidence_label'] = item
    if 'evidence_label' not in association:
        if na:
            association['evidence_label'] = 'NA'
        else:
            association['evidence_label'] = evidence

    return association
