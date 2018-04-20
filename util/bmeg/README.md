# bmeg normalizer

* normalizes the g2p index into a set of:
  * G2PAssociation
  * Feature(Variants)
  * Environment(Compound)
  * Phenotype
  * Gene


## setup

* Download the following into `genenames.tsv`

```
wget https://www.genenames.org/cgi-bin/download?col=gd_hgnc_id&col=gd_app_sym&col=gd_status&col=gd_pub_eg_id&col=gd_pub_ensembl_id&status=Approved&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&hgnc_dbtag=on&submit=submit
```

* Extract the g2p associations from elastic search see `util/elastic/split-all.sh`

## execution

*
```
$ cat ../elastic/all.json  | python normalize.py
$ ls -1 biostream/biostream/g2p/*.json
biostream/biostream/g2p/Compound.json
biostream/biostream/g2p/G2PAssociation.json
biostream/biostream/g2p/Gene.json
biostream/biostream/g2p/Phenotype.json
biostream/biostream/g2p/Variant.json
```



## vmc

```
Resolved this by following instructions at https://github.com/biocommons/biocommons.seqrepo/blob/master/doc/mirror.rst#fetching-using-rsync-manually

I rsync'd the entire repo, set instance name to master

export SEQREPO_INSTANCE_NAME=master
export SEQREPO_ROOT_DIR=/Users/walsbr/vmc-python/tests/_data/seqrepo

At that point both conversions worked.
```
