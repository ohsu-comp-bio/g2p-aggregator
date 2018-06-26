
import sys
sys.path.append('.')  # NOQA
import gene_enricher  # NOQA


def test_simple():
    tp53 = gene_enricher.get_gene('TP53')
    assert(tp53)
    assert tp53 == [{'symbol': u'TP53', 'entrez_id': u'7157',
                    'ensembl_gene_id': u'ENSG00000141510'}]


def test_simple_normalize_feature_association():
    feature_association = {'genes': ['TP53']}
    gene_enricher.normalize_feature_association(feature_association)
    assert 'gene_identifiers' in feature_association
    assert feature_association['gene_identifiers'] == [
        {'symbol': u'TP53', 'entrez_id': u'7157',
         'ensembl_gene_id': u'ENSG00000141510'}
         ]


def test_ambiguous():
    """ "ABC1" can point to both "ABCA1" and "HEATR6", """
    try:
        genes = gene_enricher.get_gene('ABC1')
        assert False, 'should have raised error'
    except ValueError as e:
        pass


def test_get_transcripts():
    transcripts = gene_enricher.get_transcripts('BRAF')
    assert len(transcripts) == 5


def test_get_transcripts_nohits():
    transcripts = gene_enricher.get_transcripts('FUBAR')
    assert len(transcripts) == 0, 'no hits should have empty array'
