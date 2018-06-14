
import sys
sys.path.append('.')  # NOQA
import gene_enricher  # NOQA


def test_simple():
    tp53 = gene_enricher.get_genes('TP53')
    assert(tp53)
    assert tp53 == [{'symbol': u'TP53', 'entrez_id': u'7157',
                    'ensembl_gene_id': u'ENSG00000141510'}]


def test_simple_normalize_feature_association():
    feature_association = {'genes': ['TP53']}
    gene_enricher.normalize_feature_association(feature_association)
    print feature_association['gene_identifiers']
    assert 'gene_identifiers' in feature_association
    assert feature_association['gene_identifiers'] == [
        {'symbol': u'TP53', 'entrez_id': u'7157',
         'ensembl_gene_id': u'ENSG00000141510'}
         ]


def test_ambiguous():
    """ "ABC1" can point to both "ABCA1" and "HEATR6", """
    genes = gene_enricher.get_genes('ABC1')
    assert genes == [
        {'symbol': u'ABCA1', 'entrez_id': u'19', 'ensembl_gene_id': u'ENSG00000165029'},
        {'symbol': u'HEATR6', 'entrez_id': u'63897', 'ensembl_gene_id': u'ENSG00000068097'}
    ]
