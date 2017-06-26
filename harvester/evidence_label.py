
# normalized vocabulary for evidence_label
# 'FDA guidelines', 'preclinical', 'trials', 'NCCN guidelines',  or
# 'European LeukemiaNet Guidelines'


def evidence_label(evidence, association, na=False):
    fda = ['fda guidelines', 'fda-approved', 'fda approved', '1']
    nccn = ['nccn guidelines', 'nccn-approved', 'nccn approved']
    eln = ['european leukemianet guidelines']
    preclinical = ['preclinical', 'pre-clinical', '2', '3']
    trials = ['early trials', 'late trials', 'phase 2',
              'phase ii', 'phase 1', 'phase i']
    cr = ['case report']

    ev_lab = {
        'FDA guidelines': fda,
        'NCCN guidelines': nccn,
        'European Leukemia Net guidelines': eln,
        'preclinical': preclinical,
        'in trials': trials,
        'case report': cr
    }

    for item in ev_lab:
        for opt in ev_lab[item]:
            if opt in evidence.lower():
                association['evidence_label'] = item
    if 'evidence_label' not in association:
        if na:
            association['evidence_label'] = 'NA'
        else:
            association['evidence_label'] = evidence

    return association
