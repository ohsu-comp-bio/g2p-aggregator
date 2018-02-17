# G2P VERSION 0.8

## contents

ui: https://g2p-test.ddns.net
elastic search backups:  s3://g2p-test-snapshots "snapshot_20180125t1305" (contact for access)
json files :  s3://g2p-0.8 (public access)


Each file is contains evidence documents from the respective source.
`all.json` contains the aggregations of all sources.


source | count
-- | --
molecularmatch_trials | 41148
jax | 5754
brca | 5717
oncokb | 4048
civic | 3497
molecularmatch | 2079
cgi | 1431
jax_trials | 1173
pmkb | 600
sage | 69


evidence_label | count
-- | --
C | 33590
D | 18764
B | 7646
A | 1715

## changes

* ontology terms (environment & phenotype) now have 'source' itemized separately
* Evidence from brca no longer has "Unreviewed" variants
* Molecular match trials CONDITION is now filtered to remove hierarchy terms, which previously accounted for many records identical except for phenotype


## structure


```
// An association between a phenotype('disease'), environment('drug')
// and genome(feature), harvested from a trusted knowledge base(source).
// For organization, the entrez name('genes') is included separately.
// For traceability, the document from the original source is included


message Evidence {
  string source = 1;
  repeated string genes = 2;

  // "ga4gh/sequence_annotations.proto"
  repeated google.protobuf.Struct features = 3;

  // "ga4gh/genotype_phenotype.proto"
  google.protobuf.Struct association = 4;

  // opaque source documents
  oneof opaque_source {
    google.protobuf.Struct cgi = 5;
    google.protobuf.Struct jax = 6;
    google.protobuf.Struct civic = 7;
    google.protobuf.Struct oncokb = 8;
    google.protobuf.Struct molecularmatch = 9;
    google.protobuf.Struct molecularmatch_trials = 10;
    google.protobuf.Struct jax_trials = 11;
    google.protobuf.Struct sage = 12;
  }  
}
```
<sub>Note: the feature and associations are based on [ga4gh.feature](https://github.com/ga4gh/ga4gh-schemas/blob/master/src/main/proto/ga4gh/sequence_annotations.proto#L30) and [ga4gh.FeaturePhenotypeAssociation](https://github.com/ga4gh/ga4gh-schemas/blob/master/src/main/proto/ga4gh/genotype_phenotype.proto#L124), but have evolved.  Future phases will create a PR to the appropriate GA4GH repository</sub>
