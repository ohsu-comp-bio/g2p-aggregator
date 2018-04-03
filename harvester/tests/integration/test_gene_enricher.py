
import sys
sys.path.append('.')  # NOQA
import gene_enricher  # NOQA


def test_simple():
    tp53 = gene_enricher.get_gene('TP53')
    assert(tp53)
    assert tp53 == {'ensembl_gene_id': u'ENSG00000141510'}
