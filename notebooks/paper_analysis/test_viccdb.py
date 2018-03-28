import pytest
from collections import Counter
from viccdb import ViccDb


@pytest.fixture(scope="module")
def vdb():
    return ViccDb(load_cache=True)


@pytest.fixture(scope="module")
def civicdb(vdb):
    return ViccDb(vdb.associations_by_source['civic'])


class TestViccDb(object):

    def test_len(self, vdb):
        assert len(vdb) > 18500

    def test_select(self, vdb, civicdb):
        assert len(civicdb) == len(vdb.select(lambda x: x['source'] == 'civic'))
        assert len(civicdb) > 1000

    def test_iter(self, vdb):
        count = 0
        for _ in vdb:
            count += 1
        assert len(vdb) == count

    def test_association_hash(self, vdb):
        c = Counter(map(lambda x: hash(x), vdb))  # Implicit test that all elements hash
        assert len(c) == sum(c.values())          # Tests that all hashes are unique

    def test_subtraction(self, vdb, civicdb):
        delta = vdb - civicdb
        assert len(delta) == len(vdb) - len(civicdb)
        assert len(delta) > 10000

class TestOncokb(object):

    def test_types(self, vdb):
        okb = vdb.associations_by_source['oncokb']
        s = set(map(lambda x: list(x['raw'].keys())[0], okb))
        assert s == set(['clinical'])