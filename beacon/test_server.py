

def test_responses(client):
    """ a populated server should return evidence for this variant """
    rsp = client.get('/responses/?chrom=2&pos=29436859&allele=C'
                     '&ref=GRCh37&beacon=civic')
    assert len(rsp.json) > 0


def test_beacons(client):
    """ a populated server should return a single beacon """
    rsp = client.get('/beacons/')
    assert len(rsp.json) == 1


def test_beacon_vicc(client):
    """ a populated server should return a single beacon """
    rsp = client.get('/beacons/vicc')
    assert rsp.json['organization'] == 'VICC, OHSU'


def test_chromosomes(client):
    """ a populated server should return evidence for this variant """
    rsp = client.get('/chromosomes')
    assert len(rsp.json) > 0
    #  assert rsp.json['organization'] == 'VICC, OHSU'
