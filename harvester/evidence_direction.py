
# normalized vocabulary for evidence_direction
# 'resistant', 'sensitive', or 'no benefit'


def evidence_direction(evidence=None, association, na=False):
    resistant = ['resistant', 'resistance', 'poor outcome',
                 'decreased response']
    sensitive = ['sensitive', 'predictive of response']
    nb = ['no benefit']

    res_type = {
        'resistant': resistant,
        'sensitive': sensitive,
        'no benefit': nb
    }

    for item in res_type:
        for opt in res_type[item]:
            if evidence and opt in evidence.lower():
                association['response_type'] = item

    if 'response_type' not in association:
        if na:
            association['response_type'] = 'NA'
        else:
            association['response_type'] = evidence

    return association
