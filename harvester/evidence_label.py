
# normalized vocabulary for evidence_label
# 'FDA guidelines', 'preclinical', 'trials', 'NCCN guidelines',  or
# 'European LeukemiaNet Guidelines'

fda = ['fda guidelines', 'fda-approved', 'fda approved']

nccn = ['nccn guidelines', 'nccn-approved', 'nccn approved']

eln = ['european leukemianet guidelines']

preclinical = ['preclinical', 'pre-clinical']

trials = ['early trials', 'late trials', 'phase 2', 'phase ii', 'phase 1', 'phase i']

cr = ['case report']

ev_lab = {
    'FDA guidelines': fda,
    'NCCN guidelines': nccn,
    'European Leukemia Net guidelines' : eln,
    'preclinical': preclinical,
    'in trials': trials,
    'case report': cr
}


