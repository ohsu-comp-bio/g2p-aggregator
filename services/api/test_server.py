
# https://beacon-network.org/#/developers/api/beacon-network
import json
import sys
import re


def test_beacons(client):
    """ a populated server should return a single beacon
    """
    rsp = client.get('/api/v1/beacon')
    rsp = json.loads(rsp.get_data())
    for k in [u'supportedReferences', u'description', u'url', u'aggregator',
              u'enabled', u'email', u'visible', u'organization', u'homePage',
              u'id', u'name']:
        assert k in rsp.keys()


def test_responses(client):
    """ a populated server should return evidence for this variant
    https://beacon-network.org/#/developers/api/beacon-network#bn-responses
    """
    rsp = client.get('/api/v1/beacon/query?referenceName=2&start=29436859&referenceBases=A&alternateBases=C&assemblyId=GRCh37')  # noqa
    rsp = json.loads(rsp.get_data())
    assert 'datasetAlleleResponses' in rsp
    datasetAlleleResponses = rsp['datasetAlleleResponses']
    assert len(datasetAlleleResponses) > 0
    datasetAlleleResponse = datasetAlleleResponses[0]
    assert 'note' in datasetAlleleResponse
    assert 'externalUrl' in datasetAlleleResponse


def test_responses_min(client):
    """ a populated server should return evidence for this variant
    https://beacon-network.org/#/developers/api/beacon-network#bn-responses
    """
    rsp = client.get('/api/v1/beacon/query?referenceName=2&start=0&startMin=29436859&startMax=29436859&referenceBases=A&alternateBases=C&assemblyId=GRCh37')  # noqa
    rsp = json.loads(rsp.get_data())
    assert 'datasetAlleleResponses' in rsp
    datasetAlleleResponses = rsp['datasetAlleleResponses']
    assert len(datasetAlleleResponses) > 0
    datasetAlleleResponse = datasetAlleleResponses[0]
    assert 'note' in datasetAlleleResponse
    assert 'externalUrl' in datasetAlleleResponse


def test_responses_max(client):
    """ a populated server should return evidence for this variant
    https://beacon-network.org/#/developers/api/beacon-network#bn-responses
    """
    rsp = client.get('/api/v1/beacon/query?referenceName=2&start=0&endMin=29436859&endMax=29436859&referenceBases=A&alternateBases=C&assemblyId=GRCh37')  # noqa
    rsp = json.loads(rsp.get_data())
    assert 'datasetAlleleResponses' in rsp
    datasetAlleleResponses = rsp['datasetAlleleResponses']
    assert len(datasetAlleleResponses) > 0
    datasetAlleleResponse = datasetAlleleResponses[0]
    assert 'note' in datasetAlleleResponse
    assert 'externalUrl' in datasetAlleleResponse


def test_externalUrl(client):
    """ a populated server should return evidence for this variant
       and the externalUrl should return the details
    """
    rsp = client.get('/api/v1/beacon/query?referenceName=2&start=29436859&referenceBases=A&alternateBases=C&assemblyId=GRCh37')  # noqa
    rsp = json.loads(rsp.get_data())
    assert 'datasetAlleleResponses' in rsp
    datasetAlleleResponses = rsp['datasetAlleleResponses']
    assert len(datasetAlleleResponses) > 0
    datasetAlleleResponse = datasetAlleleResponses[0]
    assert 'note' in datasetAlleleResponse
    assert 'externalUrl' in datasetAlleleResponse
    externalUrl = datasetAlleleResponse['externalUrl']
    match = re.match("^.*(/api.*)$", externalUrl)
    assert len(match.groups()) == 1
    # match.groups()[0]
    # >>'/api/v1/associations/bHWK6GEBSHfDESgLsEUK.'
    externalRsp = client.get(match.groups()[0])
    association = json.loads(externalRsp.get_data())
    for k in ["features", "tags",  "genes", "source", "dev_tags",
              "feature_names", "association"]:
        assert k in association.keys()


def test_associations(client):
    """ a populated server should return evidence
    """
    rsp = client.get('/api/v1/associations')  # noqa
    rsp = json.loads(rsp.get_data())
    assert len(rsp['hits']['hits']) > 0


def test_associations_size(client):
    """ a populated server should return evidence limited by size
    """
    rsp = client.get('/api/v1/associations?size=1')  # noqa
    rsp = json.loads(rsp.get_data())
    assert rsp['hits']['total'] > 1
    assert len(rsp['hits']['hits']) == 1


def test_associations_BRCA(client):
    """ a populated server should query evidence
    """
    rsp = client.get('/api/v1/associations?q=genes:BRCA&size=1')  # noqa
    rsp = json.loads(rsp.get_data())
    assert len(rsp['hits']['hits']) > 0
    assert rsp['hits']['total'] > 1
    assert len(rsp['hits']['hits']) == 1
    hit = rsp['hits']['hits'][0]
    assert 'genes' in hit
    assert 'BRCA' in hit['genes']


def test_association_terms(client):
    """ a populated server should return evidence
    """
    rsp = client.get('/api/v1/associations/terms?q=-source:*trials&f=source')  # noqa
    rsp = json.loads(rsp.get_data())
    assert 'terms' in rsp
    assert 'buckets' in rsp['terms']
    buckets = rsp['terms']['buckets']
    assert len(buckets) > 0
    for bucket in buckets:
        assert 'trials' not in bucket['key']


def test_association_terms_size(client):
    """ a populated server should return evidence
    """
    rsp = client.get('/api/v1/associations/terms?q=-source:*trials&f=source&size=1')  # noqa
    rsp = json.loads(rsp.get_data())
    print rsp
    assert 'terms' in rsp
    assert 'buckets' in rsp['terms']
    buckets = rsp['terms']['buckets']
    assert len(buckets) == 1
