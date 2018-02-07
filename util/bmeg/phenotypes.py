#!/usr/bin/python
# -*- coding: utf-8 -*-

# keep track of what we've already exported
exported = []


def phenotype_gid(p):
    """ given a phenotype, hash it"""
    """
    """
    a = []
    if 'type' in p:
        _type = p['type']
        # a.append(str(_type.get('source', '').encode('utf-8')))
        a.append(str(_type.get('id', '').encode('utf-8')))
        a.append(str(_type.get('term', '').encode('utf-8')))
        return _type.get('id')
    else:
        description = p.get('description', None)
        a.append(description)
        return 'phenotype:' + ':'.encode('utf-8').join(a)


def bmeg_phenotype(phenotype, gid):
    p = {'type': {'term_id': gid}}
    if 'type' in phenotype:
        p['type']['term'] = phenotype['type']['term']
    if 'family' in phenotype:
        p['family'] = phenotype['family']
    if 'description' in phenotype:
        p['description'] = phenotype['description']
    return p


def normalize(hit):
    """ returns a tuple of (hit, phenotypes), where hit has been modified to
    normalize hit.phenotype.  The phenotypes[] array
    contains phenotypes observed in this hit that have not yet been returned
    """
    phenotypes = {}
    # hash each phenotype
    if 'phenotype' in hit['association']:
        gid = phenotype_gid(hit['association']['phenotype'])
        phenotypes[gid] = bmeg_phenotype(hit['association']['phenotype'], gid)
        hit['association']['phenotypes'] = list(phenotypes.keys())
        for k in phenotypes.keys():
            if str(k) in exported:
                del phenotypes[k]
        exported.extend(phenotypes.keys())
        del hit['association']['phenotype']
    return (hit, phenotypes)
