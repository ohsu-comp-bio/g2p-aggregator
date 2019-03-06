# COSMIC Mutation Data; can download from https://grch37-cancer.sanger.ac.uk/cosmic/download
# Note: we want GrCh37 build for now since most databases use this build.
# https://grch37-cancer.sanger.ac.uk/cosmic/files?data=/files/grch37/cosmic/v81/CosmicMutantExport.tsv.gz
COSMIC_MUTATIONS=CosmicMutantExport.tsv.gz

BENCHMARK_DATASET=oncokb

CGI_VERSION=20170208

all: oncokb_all_actionable_variants.tsv cgi_biomarkers_per_variant.tsv \
		cosmic_lookup_table.tsv cgi_mut_benchmarking.tsv oncokb_mut_benchmarking.tsv \
		benchmark_results.txt \
		proteins

## Do bulk download of OncoKB and set up TSV for ingestion.
oncokb_all_actionable_variants.tsv:
	curl -o oncokb_all_actionable_variants_$(shell date +"%Y%m%d").tsv http://oncokb.org/api/v1/utils/allActionableVariants.txt
	cp oncokb_all_actionable_variants_$(shell date +"%Y%m%d").tsv ../data/oncokb_allActionableVariants.txt

## Do bulk download of OncoKB annotated variants for harvester
oncokb_all_annotated_variants.tsv:
	curl -o oncokb_all_annotated_variants_$(shell date +"%Y%m%d").tsv https://oncokb.org/api/v1/utils/allAnnotatedVariants.txt
	cp oncokb_all_annotated_variants_$(shell date +"%Y%m%d").tsv ../data/oncokb_allAnnotatedVariants.txt

## Do bulk download of CGI and set up TSV for ingestion.
cgi_biomarkers_per_variant.tsv:
	mkdir cgi_biomarkers_latest
	cd cgi_biomarkers_latest && \
	curl -Ok https://www.cancergenomeinterpreter.org/data/cgi_biomarkers_latest.zip && \
	unzip cgi_biomarkers_latest.zip
	cp cgi_biomarkers_latest/cgi_biomarkers_per_variant.tsv .

## Create COSMIC lookup table suitable for annotating variants with chrom/start/end/ref/alt
cosmic_lookup_table.tsv:
	gzcat $(COSMIC_MUTATIONS) | tail -n +2 | python cosmic_lookup_table.py create_table > temp.tsv
	(head -n 1 temp.tsv ; tail -n +2 temp.tsv | sort | uniq) > cosmic_lookup_table.tsv
	rm -f temp.tsv

## Create lookup tables for proteins
proteins:
	mkdir -p ../data/proteins/
	wget -r -l1 -np -nd "ftp://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/mRNA_Prot/" -P ../data/proteins -A "human.*.protein.faa.gz"

## Create cgi_mut_benchmarking.tsv file.
cgi_mut_benchmarking.tsv:
	grep MUT cgi_biomarkers_20170208.tsv | \
	egrep -v "oncogenic mutation|insertion|deletion|wildtype|promoters|_variant" | \
	cut -f4 | sed 's/\:/	/g' > cgi_mut_benchmarking.tsv

## Create oncokb_mut_benchmarking.tsv file.
oncokb_mut_benchmarking.tsv: oncokb_all_actionable_variants.tsv
	cut -f1-2 oncokb_all_actionable_variants.tsv | \
	egrep -v "del|ins|Fusion|Oncogenic|mutations|dup|Wildtype|Amplification|Truncating|splice" \
	> oncokb_mut_benchmarking.tsv

## Benchmark file.
benchmark_results.txt: cosmic_lookup_table.tsv $(BENCHMARK_DATASET)_mut_benchmarking.tsv
	 python cosmic_lookup_table.py benchmark --lookup-file cosmic_lookup_table.tsv \
	 	--benchmark-file $(BENCHMARK_DATASET)_mut_benchmarking.tsv > benchmark_results.txt

$(COSMIC_MUTATIONS):
	echo you will need to register and download https://grch37-cancer.sanger.ac.uk/cosmic/files?data=/files/grch37/cosmic/v81/CosmicMutantExport.tsv.gz

clean:
	rm -rf cosmic_lookup_table.tsv cgi_mut_benchmarking.tsv oncokb_mut_benchmarking.tsv benchmark.txt \
	cgi_biomarkers_$(CGI_VERSION) cgi_biomarkers_per_variant.tsv \
	oncokb_all_actionable_variants*.tsv
