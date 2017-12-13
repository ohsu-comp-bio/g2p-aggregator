import sys
sys.path.append('.')  # NOQA

from reference_genome_normalizer import normalize_feature_association


def _build_feature_association(referenceName):
    feature_association = {}
    feature_association['features'] = [{'referenceName': referenceName}]
    return feature_association


def _test(referenceName, expected):
    feature_association = _build_feature_association(referenceName)
    normalize_feature_association(feature_association)
    assert (feature_association['features'][0]['referenceName'] == expected)


def test_None():
    _test(None, None)


def test_37():
    _test(37, 'GRCh37')


def test_37Str():
    _test('37', 'GRCh37')


def test_GRCh37():
    _test('GRCh37', 'GRCh37')


def test_GRCh37hg19():
    _test('GRCh37/hg19', 'GRCh37')


def test_GRCh38():
    _test('GRCh38', 'GRCh38')


def test_38():
    _test(38, 'GRCh38')


def test_38Str():
    _test('38', 'GRCh38')


def test_Hg38():
    _test('Hg38', 'GRCh38')


def test_grch37_hg19():
    _test('grch37_hg19', 'GRCh37')
