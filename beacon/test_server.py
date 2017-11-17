
# https://beacon-network.org/#/developers/api/beacon-network


def test_beacons(client):
    """ a populated server should return a single beacon
        https://beacon-network.org/#/developers/api/beacon-network#bn-beacons
    """
    rsp = client.get('/beacons/')
    assert len(rsp.json) == 1
    b = rsp.json[0]
    for k in [u'supportedReferences', u'description', u'url', u'aggregator',
              u'enabled', u'email', u'visible', u'organization', u'homePage',
              u'id', u'name']:
        assert k in b.keys()


def test_beacon_vicc(client):
    """ a populated server should return a single beacon """
    rsp = client.get('/beacons/vicc')
    assert rsp.json['organization'] == 'VICC'


def test_beacon_organizations(client):
    """ a populated server should return a single beacon
        https://beacon-network.org/api/organizations
    """
    rsp = client.get('/organizations')
    assert len(rsp.json) == 1
    assert rsp.json[0]["id"] == "vicc"


def test_responses(client):
    """ a populated server should return evidence for this variant
    https://beacon-network.org/#/developers/api/beacon-network#bn-responses
    """
    rsp = client.get('/responses/?chrom=2&pos=29436859&allele=C'
                     '&ref=GRCh37&beacon=vicc')
    assert len(rsp.json) > 0


def test_chromosomes(client):
    """ a populated server should return evidence for these chromosomes
        https://beacon-network.org/#/developers/api/beacon-network#bn-chromosomes
    """
    rsp = client.get('/chromosomes')
    assert len(rsp.json) > 0
    chromosomes = rsp.json
    for chromosome in [u'13', u'17', u'7', u'2', u'12', u'3', u'9', u'4',
                       u'10', u'1']:
        assert chromosome in chromosomes


def test_references(client):
    """ a populated server should return evidence for these references
        https://beacon-network.org/#/developers/api/beacon-network#bn-references
    """
    rsp = client.get('/references')
    assert len(rsp.json) > 0
    references = rsp.json
    assert references == [u'GRCh37']


def test_alleles(client):
    """ a populated server should return evidence for these alleles
        https://beacon-network.org/#/developers/api/beacon-network#bn-alleles
    """
    rsp = client.get('/alleles')
    assert len(rsp.json) > 0
    alleles = rsp.json
    for allele in [u'C', u'G', u'A', u'T', u'AC', u'CC', u'CT', u'AT']:
        assert allele in alleles
