import pytest
from collections import Counter


@pytest.fixture(scope="module")
def vdb():
    from viccdb import ViccDb
    return ViccDb(load_cache=True)


class TestViccDb(object):

    def test_len(self, vdb):
        assert len(vdb) > 18500

    def test_select(self, vdb):
        assert len(vdb.associations_by_source['civic']) == len(vdb.select(lambda x: x['source'] == 'civic'))
        assert len(vdb.associations_by_source['civic']) > 1000

    def test_iter(self, vdb):
        count = 0
        for _ in vdb:
            count += 1
        assert len(vdb) == count

    def test_association_hash(self, vdb):
        c = Counter(map(lambda x: hash(x), vdb))  # Implicit test that all elements hash
        assert len(c) == sum(c.values())          # Tests that all hashes are unique


class TestOncokb(object):

    def test_types(self, vdb):
        okb = vdb.associations_by_source['oncokb']
        s = set(map(lambda x: list(x['raw'].keys())[0], okb))
        assert s == set(['clinical'])