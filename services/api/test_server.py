
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
    print 'rsp', rsp
    assert 'terms' in rsp
    assert 'buckets' in rsp['terms']
    buckets = rsp['terms']['buckets']
    assert len(buckets) == 1


def test_features_associations(client):
    """ a populated server should return evidence
    """

    p204 = [{'end': 41266125L, 'name': 'CTNNB1 p.T41I', 'start': 41266125L, 'biomarker_type': 'Missense_Mutation', 'referenceName': '3', 'geneSymbol': 'CTNNB1', 'alt': 'T', 'ref': 'C', 'chromosome': '3', 'description': 'catenin (cadherin-associated protein), beta 1, 88kDa'}, {'end': 142188239L, 'name': 'ATR p.I2164M', 'start': 142188239L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'ATR', 'alt': 'C', 'ref': 'T', 'chromosome': '3', 'description': 'ATR serine/threonine kinase'}, {'end': 89685310L, 'name': 'PTEN p.-70fs', 'start': 89685309L, 'biomarker_type': 'Frame_Shift_Ins', 'referenceName': 'GRCh37', 'geneSymbol': 'PTEN', 'alt': 'AATCT', 'ref': '-', 'chromosome': '10', 'description': 'phosphatase and tensin homolog'}, {'end': 41266125L, 'name': 'CTNNB1 p.T41I', 'start': 41266125L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'CTNNB1', 'alt': 'T', 'ref': 'C', 'chromosome': '3', 'description': 'catenin (cadherin-associated protein), beta 1, 88kDa'}, {'end': 1584977L, 'name': 'P2RY8 p.A159T', 'start': 1584977L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'P2RY8', 'alt': 'T', 'ref': 'C', 'chromosome': 'X', 'description': 'purinergic receptor P2Y, G-protein coupled, 8'}, {'end': 170802031L, 'name': 'TNIK p.T1028A', 'start': 170802031L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'TNIK', 'alt': 'C', 'ref': 'T', 'chromosome': '3', 'description': 'TRAF2 and NCK interacting kinase'}, {'end': 118764345L, 'name': 'CXCR5 p.S31F', 'start': 118764345L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'CXCR5', 'alt': 'T', 'ref': 'C', 'chromosome': '11', 'description': 'chemokine (C-X-C motif) receptor 5'}, {'end': 136071095L, 'name': 'ZRANB3 p.L310F', 'start': 136071095L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'ZRANB3', 'alt': 'G', 'ref': 'C', 'chromosome': '2', 'description': 'zinc finger, RAN-binding domain containing 3'}, {'end': 228566043L, 'name': 'OBSCN p.V8839A', 'start': 228566043L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'OBSCN', 'alt': 'C', 'ref': 'T', 'chromosome': '1', 'description': 'obscurin, cytoskeletal calmodulin and titin-interacting RhoGEF'}, {'end': 2097401L, 'name': 'STK35 p.L328V', 'start': 2097401L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'STK35', 'alt': 'G', 'ref': 'C', 'chromosome': '20', 'description': 'serine/threonine kinase 35'}, {'end': 58130871L, 'name': 'AGAP2 p.A387T', 'start': 58130871L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'AGAP2', 'alt': 'T', 'ref': 'C', 'chromosome': '12', 'description': 'ArfGAP with GTPase domain, ankyrin repeat and PH domain 2'}, {'end': 33690771L, 'name': 'IP6K3 p.R320H', 'start': 33690771L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'IP6K3', 'alt': 'T', 'ref': 'C', 'chromosome': '6', 'description': 'inositol hexakisphosphate kinase 3'}, {'end': 101910837L, 'name': 'NALCN p.G408A', 'start': 101910837L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'NALCN', 'alt': 'G', 'ref': 'C', 'chromosome': '13', 'description': 'sodium leak channel, non-selective'}, {'end': 57424051L, 'name': 'MYO1A p.R845K', 'start': 57424051L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'MYO1A', 'alt': 'T', 'ref': 'C', 'chromosome': '12', 'description': 'myosin IA'}, {'end': 38211533L, 'name': 'TRPC4 p.R814K', 'start': 38211533L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'TRPC4', 'alt': 'T', 'ref': 'C', 'chromosome': '13', 'description': 'transient receptor potential cation channel, subfamily C, member 4'}, {'end': 32257834L, 'name': 'SPOCD1 p.R982C', 'start': 32257834L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'SPOCD1', 'alt': 'A', 'ref': 'G', 'chromosome': '1', 'description': 'SPOC domain containing 1'}, {'end': 28097282L, 'name': 'ZSCAN16 p.E201K', 'start': 28097282L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'ZSCAN16', 'alt': 'A', 'ref': 'G', 'chromosome': '6', 'description': 'zinc finger and SCAN domain containing 16'}, {'end': 84628811L, 'name': 'SEMA3D p.R760Q', 'start': 84628811L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'SEMA3D', 'alt': 'T', 'ref': 'C', 'chromosome': '7', 'description': 'sema domain, immunoglobulin domain (Ig), short basic domain, secreted, (semaphorin) 3D'}, {'end': 72400932L, 'name': 'NEGR1 p.A80V', 'start': 72400932L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'NEGR1', 'alt': 'A', 'ref': 'G', 'chromosome': '1', 'description': 'neuronal growth regulator 1'}, {'end': 35778772L, 'name': 'ARPP21 p.P521L', 'start': 35778772L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'ARPP21', 'alt': 'T', 'ref': 'C', 'chromosome': '3', 'description': 'cAMP-regulated phosphoprotein, 21kDa'}, {'end': 21016738L, 'name': 'KIF17 p.R442S', 'start': 21016738L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'KIF17', 'alt': 'T', 'ref': 'G', 'chromosome': '1', 'description': 'kinesin family member 17'}, {'end': 51929267L, 'name': 'IQCF1 p.R86Q', 'start': 51929267L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'IQCF1', 'alt': 'T', 'ref': 'C', 'chromosome': '3', 'description': 'IQ motif containing F1'}, {'end': 95188799L, 'name': 'CDH17 p.E132K', 'start': 95188799L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'CDH17', 'alt': 'T', 'ref': 'C', 'chromosome': '8', 'description': 'cadherin 17, LI cadherin (liver-intestine)'}, {'end': 96117712L, 'name': 'CCDC82 p.L67P', 'start': 96117712L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'CCDC82', 'alt': 'G', 'ref': 'A', 'chromosome': '11', 'description': 'coiled-coil domain containing 82'}, {'end': 105967614L, 'name': 'AASDHPPT p.R304*', 'start': 105967614L, 'biomarker_type': 'Nonsense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'AASDHPPT', 'alt': 'T', 'ref': 'C', 'chromosome': '11', 'description': 'aminoadipate-semialdehyde dehydrogenase-phosphopantetheinyl transferase'}, {'end': 31538698L, 'name': 'CLDN17 p.A80S', 'start': 31538698L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'CLDN17', 'alt': 'A', 'ref': 'C', 'chromosome': '21', 'description': 'claudin 17'}, {'end': 38483424L, 'name': 'UTP11L p.M70I', 'start': 38483424L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'UTP11L', 'alt': 'A', 'ref': 'G', 'chromosome': '1', 'description': 'UTP11-like, U3 small nucleolar ribonucleoprotein (yeast)'}, {'end': 155526050L, 'name': 'FGG p.Q433P', 'start': 155526050L, 'biomarker_type': 'Splice_Site', 'referenceName': 'GRCh37', 'geneSymbol': 'FGG', 'alt': 'G', 'ref': 'T', 'chromosome': '4', 'description': 'fibrinogen gamma chain'}, {'end': 148617051L, 'name': 'ABLIM3 p.A310V', 'start': 148617051L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'ABLIM3', 'alt': 'T', 'ref': 'C', 'chromosome': '5', 'description': 'actin binding LIM protein family, member 3'}, {'end': 31895941L, 'name': 'CFB p.P86S', 'start': 31895941L, 'biomarker_type': 'Splice_Site', 'referenceName': 'GRCh37', 'geneSymbol': 'CFB', 'alt': 'T', 'ref': 'C', 'chromosome': '6', 'description': 'complement factor B'}, {'end': 18051501L, 'name': 'MYO15A p.A2223V', 'start': 18051501L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'MYO15A', 'alt': 'T', 'ref': 'C', 'chromosome': '17', 'description': 'myosin XVA'}, {'end': 60969271L, 'name': 'CABLES2 p.S219C', 'start': 60969271L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'CABLES2', 'alt': 'C', 'ref': 'G', 'chromosome': '20', 'description': 'Cdk5 and Abl enzyme substrate 2'}, {'end': 186096984L, 'name': 'KIAA1430 p.L426F', 'start': 186096984L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'KIAA1430', 'alt': 'A', 'ref': 'G', 'chromosome': '4', 'description': ''}, {'end': 110056501L, 'name': 'FIG4 p.G216R', 'start': 110056501L, 'biomarker_type': 'Splice_Site', 'referenceName': 'GRCh37', 'geneSymbol': 'FIG4', 'alt': 'A', 'ref': 'G', 'chromosome': '6', 'description': 'FIG4 phosphoinositide 5-phosphatase'}, {'end': 67690336L, 'name': 'RLTPR p.C1275Y', 'start': 67690336L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'RLTPR', 'alt': 'A', 'ref': 'G', 'chromosome': '16', 'description': 'RGD motif, leucine rich repeats, tropomodulin domain and proline-rich containing'}, {'end': 67702418L, 'name': 'C16orf86 p.D290G', 'start': 67702418L, 'biomarker_type': 'Missense_Mutation', 'referenceName': 'GRCh37', 'geneSymbol': 'C16orf86', 'alt': 'G', 'ref': 'A', 'chromosome': '16', 'description': 'chromosome 16 open reading frame 86'}]

    dataset_features = p204

    # json.dumps({'queryFeatures': features})
    print json.dumps([p204[0]])
    rsp = client.post('/api/v1/features/associations',
                      data=json.dumps([p204[0]]),
                      content_type='application/json')
    rsp = json.loads(rsp.get_data())
    assert len(rsp) > 0
    print 'results'
    for q in rsp:
        print q['allele'], q['name'], q['biomarker_type'], len(q['hits'])  # , q['query_string']
