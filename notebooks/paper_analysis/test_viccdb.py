import pytest
from collections import Counter
from viccdb import ViccDb


@pytest.fixture(scope="module")
def vdb():
    vdb = ViccDb()
    omit = vdb.select(lambda x: x['source'] == 'oncokb' and 'clinical' not in x['raw'])
    return vdb - omit


@pytest.fixture(scope="module", params=['molecularmatch', 'brca', 'civic', 'pmkb', 'oncokb', 'jax', 'cgi'])
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


class TestOncokb(object):

    def test_types(self, vdb):
        okb = vdb.by_source('oncokb')
        for x in okb:
            assert 'clinical' in x['raw'] # Only clinical results

class TestSource(object):

    def test_hash(self, sourcedb):
        c = Counter(map(lambda x: hash(x), sourcedb))   # Implicit test that all elements hash
        assert len(c) <= sum(c.values()) + 5               # Tests that most hashes are unique (within 5 collisions)

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
        assert count < 25

    def test_diseases(self, sourcedb):
        count = 0
        for x in sourcedb:
            if x.disease is None:
                count += 1
        assert count < 5

    def test_drugs(self, sourcedb):
        count = 0
        for x in sourcedb:
            if len(x.drugs) == 0:
                count += 1
        assert count == 0