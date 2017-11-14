from flask import Flask, jsonify
from flasgger import Swagger
from flask import request

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A


app = Flask(__name__)
swagger = Swagger(app)


# see https://beacon-network.org/#/developers/api/beacon-network

# Beacon Network exposes XML and JSON APIs, where a particular response format
# can be requested by providing the "Accept" header with your HTTP request
# (e.g. Accept: application/json). The system exposes the following endpoints
# accessible through HTTP GET requests:
#
# Endpoint	Description	Example
# /beacons	Lists beacons.	Go to example
# /beacons/{beacon}	Shows a beacon.	Go to example
# /organizations	Lists organizations.	Go to example
# /organizations/{organization}	Shows an organization.	Go to example
# /responses	Queries beacons.	Go to example
# /responses/{beacon}	Queries a beacon.	Go to example
# /chromosomes	Lists supported chromosome.	Go to example
# /alleles	Lists supported alleles.	Go to example
# /references	Lists supported reference genomes.	Go to example

VICC_BEACON = {
    "id": "vicc",
    "name": "VICC - G2P",
    "url": None,
    "organization": "VICC, OHSU",
    "description": """
    The Variant Interpretation for Cancer Consortium (VICC)
The VICC is a Driver Project of the Global Alliance for Genomics Health (GA4GH).

The field of precision medicine aspires to a future in which a cancer patient’s molecular information can be used to inform diagnosis, prognosis and treatment options most likely to benefit that individual patient. Many groups have created knowledgebases to annotate cancer genomic mutations associated with evidence of pathogenicity or relevant treatment options. However, clinicians and researchers are unable to fully utilize the accumulated knowledge derived from such efforts. Integration of the available knowledge is currently infeasible because each group (often redundantly) curates their own knowledgebase without adherence to any interoperability standards. Therefore, there is a clear need to standardize and coordinate clinical-genomics curation efforts, and create a public community resource able to query the aggregated information. To this end we have formed the Variant Interpretation for Cancer Consortium (VICC) to bring together the leading institutions that are independently developing comprehensive cancer variant interpretation databases.
""",
    "homePage": "http://cancervariants.org/",
    "email": None,
    "aggregator": True,
    "visible": True,
    "enabled": True,
    "supportedReferences": [
      "GRCH37"
    ]
}

VICC_ORG = {
    "id": "vicc",
    "name": "VICC - G2P"
}


@app.route('/beacons/')
def beacons():
    """
    List beacons. Takes no parameters
    ---
    responses:
      200:
        description: An array of beacons
    """
    beaconsList = [VICC_BEACON]
    return (jsonify(beaconsList))


@app.route('/beacons/<id>')
def beacon(id):
    """
    return our beacon
    ---
    parameters:
      - name: id
        in: path
        type: string
        enum: ['vicc']
        required: true
        default: vicc

    responses:
      200:
        description: A beacon
    """
    if (id == "vicc"):
        return (jsonify(VICC_BEACON))
    abort(404)


@app.route('/organizations/')
def organizations():
    """
    List organizations. Takes no parameters
    ---
    responses:
      200:
        description: An array of organizations
    """
    organizationsList = [VICC_ORG]
    return (jsonify(organizationsList))


@app.route('/organization/<id>')
def organization(id):
    """
    List organization. Takes organization id.
    ---
    parameters:
      - name: id
        in: path
        type: string
        enum: ['vicc']
        required: true
        default: vicc

    responses:
      200:
        description: An organization
    """
    if (id == "vicc"):
        return (jsonify(VICC_ORG))
    abort(404)


@app.route('/responses/')
def responses():
    """
    List hits. Takes a variant coordinate as info
    ---
    parameters:
      - name: chrom
        in: query
        type: string
        required: true
        description: "Chromosome ID. Accepted values: 1-22, X, Y, MT. Note: For compatibility with conventions set by some of the existing beacons, an arbitrary prefix is accepted as well (e.g. chr1 is equivalent to chrom1 and 1)."
      - name: pos
        in: query
        type: number
        description: "Coordinate within a chromosome. Position is a number and is 0-based."
      - name: allele
        in: query
        type: string
        description: "Any string of nucleotides A,C,T,G or D, I for deletion and insertion, respectively. Note: For compatibility with conventions set by some of the existing beacons, DEL and INS identifiers are also accepted."
      - name: ref
        in: query
        type: string
        description: "Genome ID. If not specified, all the genomes supported by the given beacons are queried. Note: For compatibility with conventions set by some of the existing beacons, both GRC or HG notation are accepted, case insensitive. Optional parameter."
      - name: beacon
        in: query
        type: string
        description: "Beacon IDs. If specified, only beacons with the given IDs are queried. Responses from all the supported beacons are obtained otherwise. Format: [id1,id2]. Optional parameter."
    responses:
      200:
        description: An array of hits
    """
    client = Elasticsearch()
    s = Search(using=client)
    args = ['chrom', 'pos', 'allele', 'ref', 'beacon']
    alias = ['features.chromosome', 'features.start', 'features.alt',
             'features.referenceName', 'source']

    q = s
    queryEcho = {}
    # build parameters for query, and echo query to response
    for idx, arg in enumerate(args):
        value = request.args.get(arg, None)
        if value:
            kwargs = {}
            queryEcho[arg] = value
            kwargs[alias[idx]] = value
            q = q.query("match", **kwargs)

    responses = []
    for hit in q:
        response = {
            "beacon": VICC_BEACON,
            "query": queryEcho,
            "response": True,
            "externalUrl": "//TODO---",
            "info": hit.to_dict()
        }
        responses.append(response)
    return (jsonify(responses))


@app.route('/chromosomes')
def chromosomes():
    client = Elasticsearch()
    s = Search(using=client, index="associations")
    s.aggs.bucket('chromosome', 'terms', field='features.chromosome.keyword')
    aggregation = s.execute()
    # print aggregation.aggregations.chromosome # .doc_count
    # print aggregation.hits.total
    # print aggregation.aggregations.chromosome.buckets
    responses = []
    for bucket in aggregation.aggregations.chromosome.buckets:
        responses.append(bucket.to_dict())
    return (jsonify(responses))

#  MAIN -----------------
if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True)
