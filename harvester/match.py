
# normalized vocabulary for evidence_label
# 'FDA guidelines', 'preclinical', 'trials', 'NCCN guidelines',  or
# 'European LeukemiaNet Guidelines'

fda = ['fda guidelines', 'fda-approved', 'fda approved']

nccn = ['nccn guidelines', 'nccn-approved', 'nccn approved']

eln = ['european leukemianet guidelines']

preclinical = ['preclinical', 'pre-clinical']

trials = ['early trials', 'phase 2', 'phase ii', 'phase 1', 'phase i']

ev_lab = {
    'FDA guidelines': fda,
    'NCCN guidelines': nccn,
    'European Leukemia Net guidelines' : eln,
    'preclinical': preclinical,
    'in trials': trials
}

# normalized vocabulary for response_type
# 'resistant', 'sensitive', or 'no benefit'

resistant = ['resistant', 'resistance', 'poor outcome', 'decreased response']

sensitive = ['sensitive', 'predictive of response']

nb = ['no benefit']

res_type = {
    'resistant': resistant,
    'sensitive': sensitive,
    'no benefit' : nb
}

