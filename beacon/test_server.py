
# https://beacon-network.org/#/developers/api/beacon-network
import json


def test_beacons(client):
    """ a populated server should return a single beacon
        https://beacon-network.org/#/developers/api/beacon-network#bn-beacons
    """
    rsp = client.get('/beacons/')
    rsp = json.loads(rsp.get_data())
    assert len(rsp) == 1
    b = rsp[0]
    for k in [u'supportedReferences', u'description', u'url', u'aggregator',
              u'enabled', u'email', u'visible', u'organization', u'homePage',
              u'id', u'name']:
        assert k in b.keys()


def test_beacon_vicc(client):
    """ a populated server should return a single beacon """
    rsp = client.get('/beacons/vicc')
    rsp = json.loads(rsp.get_data())
    assert rsp['organization'] == 'VICC'


def test_beacon_organizations(client):
    """ a populated server should return a single beacon
        https://beacon-network.org/api/organizations
    """
    rsp = client.get('/organizations')
    rsp = json.loads(rsp.get_data())
    assert len(rsp) == 1
    assert rsp[0]["id"] == "vicc"


def test_responses(client):
    """ a populated server should return evidence for this variant
    https://beacon-network.org/#/developers/api/beacon-network#bn-responses
    """
    rsp = client.get('/responses/?chrom=2&pos=29436859&allele=C'
                     '&ref=GRCh37&beacon=vicc')
    rsp = json.loads(rsp.get_data())
    assert len(rsp) > 0


def test_chromosomes(client):
    """ a populated server should return evidence for these chromosomes
        https://beacon-network.org/#/developers/api/beacon-network#bn-chromosomes
    """
    rsp = client.get('/chromosomes')
    rsp = json.loads(rsp.get_data())
    assert len(rsp) > 0
    chromosomes = rsp
    for chromosome in [u'13', u'17', u'7', u'2', u'12', u'3', u'9', u'4',
                       u'10', u'1']:
        assert chromosome in chromosomes


def test_references(client):
    """ a populated server should return evidence for these references
        https://beacon-network.org/#/developers/api/beacon-network#bn-references
    """
    rsp = client.get('/references')
    rsp = json.loads(rsp.get_data())
    assert len(rsp) > 0
    references = rsp
    assert references == [u'GRCh37']


def test_alleles(client):
    """ a populated server should return evidence for these alleles
        https://beacon-network.org/#/developers/api/beacon-network#bn-alleles
    """
    rsp = client.get('/alleles')
    rsp = json.loads(rsp.get_data())
    assert len(rsp) > 0
    alleles = rsp
    for allele in [u'C', u'G', u'A', u'T', u'-', u'AC', u'CC', u'CT', u'TG']:
        assert allele in alleles
