
# Search Examples:

The G2P datastore has been extensively normalized, denormalized and tagged to make it easier to find what you want.

Lets assume you are interested in "EGFR mutations interpretations in lung adenocarcinoma"

* In general:
  * Simply enter keywords: `EGFR lung adenocarcinoma` will search with a default "OR" and returns approximately 13K hits.
  * Keywords can be grouped using double quotes: `EGFR "lung adenocarcinoma"` will return approximately 8.9K hits.
  * Logical grouping are supported using parenthesis, AND, OR: `EGFR AND "lung adenocarcinoma"` will return approximately 1.8K hits,  `(EGFR AND CYP3A) AND "lung adenocarcinoma"` will return 1 hit.

* More specifically:
  * G2P associations are decorated with various ontology terms:
    * Phenotypes are tagged with disease ontology identifiers: "lung adenocarcinoma"  is tagged with "DOID:0050615"
    * Genes are tagged with ensemble identifiers: "EGFR"  is tagged with "ENSG00000146648"
    * Features are tagged with sequence ontology identifiers: "substitution" is tagged with "SO:1000002"
    * ClinVar's allele registry is used to tag features with hgvs synonyms: [NC_000009.12:g.130872896C>T, NG_012034.1:g.164016C>T, ...]
  * Field limited searches:
    * The document's fields can be used to search within specific fields: `gene_identifiers.ensembl_gene_id:ENSG00000146648`
    * Fields searches can be further optimized by using the keyword modifier to match exact terms: `gene_identifiers.ensembl_gene_id.keyword:ENSG00000146648`
    * The field names are provided document mapping is available at the `/associations` endpoint
