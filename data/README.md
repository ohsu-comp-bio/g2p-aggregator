# data

## overview

This directory contains the 'raw' files from various sources necessary for g2p harvesting.

## contents

* [pmkb_interpretations.json](https://s3-us-west-2.amazonaws.com/g2p-0.7/unprocessed-files/pmkb_interpretations.json)
  * manual download
  * raw interpretations from cornell linda at standardmolecular dot com

* [molecularmatch_trials.json](https://s3-us-west-2.amazonaws.com/g2p-0.7/unprocessed-files/molecularmatch_trials.json)
  * pre-harmonization download of molecularmatch trials
  * recreate  via `python harvester.py --silos file --harvesters molecularmatch_trials  --phases harvest`

* cgi
  * [cgi_biomarkers_per_variant.tsv](https://www.cancergenomeinterpreter.org/biomarkers)
  * [catalog_of_validated_oncogenic_mutations.tsv](https://www.cancergenomeinterpreter.org/mutations)
  * manual download
  * raw evidence

* [allAnnotatedVariants.txt](http://oncokb.org/api/v1/utils/allAnnotatedVariants.txt), [allActionableVariants.txt](http://oncokb.org/api/v1/utils/allActionableVariants.txt)
  * download by clicking link, or going to [oncokb.org/#/dataAccess](http://oncokb.org/#/dataAccess)
  * used to run harvester on oncokb
  * 'oncokb\_' prefix added to files for clarity

* [data_mutations_extended_1.0.1.txt,data_clinical_1.0.1.txt](https://www.synapse.org/#!Synapse:syn7851250 )
  * manual registration and download
  * cohort for GENIE analysis notebook

* [harvester/cosmic_lookup_table.tsv](https://grch37-cancer.sanger.ac.uk/cosmic/files?data=/files/grch37/cosmic/v81/CosmicMutantExport.tsv.gz)
  * manual download
  * pre processing done by harvester/Makefile including [harvester/oncokb_all_actionable_variants.tsv](http://oncokb.org/api/v1/utils/allActionableVariants.txt)

* [msk_impact_2017/*](http://www.cbioportal.org/study?id=msk_impact_2017#summary)
  * manual download  from 'Download Data' button at top of page
  * cohort for GENIE analysis notebook
