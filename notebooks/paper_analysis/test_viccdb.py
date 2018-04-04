import pytest
from collections import Counter
from viccdb import ViccDb
from os import environ


CACHE_PRESENT = ViccDb.DEFAULT_CACHE.exists()
PAPER_TESTING = bool(environ['VICC_PAPER_TESTING'])
if PAPER_TESTING:
    SOURCES = ['molecularmatch', 'civic', 'pmkb', 'oncokb', 'jax', 'cgi']
else:
    SOURCES = ['molecularmatch', 'civic', 'pmkb', 'brca', 'oncokb', 'jax', 'cgi']


@pytest.fixture(scope="module")
def vdb():
    vdb = ViccDb(load_cache=CACHE_PRESENT)
    return vdb


@pytest.fixture(scope="module", params=SOURCES)
def sourcedb(vdb, request):
    return ViccDb(vdb.by_source(request.param))


class TestViccDb(object):

    def test_len(self, vdb):
        assert len(vdb) > 5000

    def test_select(self, vdb):
        civicdb = vdb.by_source('civic')
        assert len(civicdb) == len(vdb.select(lambda x: x['source'] == 'civic'))
        assert len(civicdb) > 1000

    def test_iter(self, vdb):
        count = 0
        for _ in vdb:
            count += 1
        assert len(vdb) == count

    def test_subtraction(self, vdb):
        civicdb = vdb.by_source('civic')
        delta = vdb - civicdb
        assert len(delta) == len(vdb) - len(civicdb)
        assert len(delta) > 5000

    def test_search_features(self, vdb):
        results = vdb.search_features(chromosome=7, start=140453136, end=140453136, reference_name='GRCh37')  # BRAF V600E
        assert len(results) >= 500
        assert len(results.sources) >= 5


class TestOncokb(object):

    def test_types(self, vdb):
        okb = vdb.by_source('oncokb')
        for x in okb:
            assert 'clinical' in x['raw']  # Only clinical results


class TestSource(object):

    def test_hash(self, sourcedb):
        c = Counter(map(lambda x: hash(x), sourcedb))   # Implicit test that all elements hash
        assert len(c) == sum(c.values())             # Tests that hashes are unique

    def test_genes(self, sourcedb):
        count = 0
        for x in sourcedb:
            if len(x.genes) == 0:
                count += 1
        assert count == 0

    def test_features(self, sourcedb):
        count = 0
        for x in sourcedb:
            if len(x.features) == 0:
                count += 1
        assert count < 0.02 * len(sourcedb)  # less than 2% of associations lacking features

    def test_diseases(self, sourcedb):
        count = 0
        for x in sourcedb:
            if x.disease is None:
                count += 1
        assert count < 5

    # def test_drugs(self, sourcedb):
    #     count = 0
    #     for x in sourcedb:
    #         if len(x.drugs) == 0:
    #             count += 1
    #     assert count == 0