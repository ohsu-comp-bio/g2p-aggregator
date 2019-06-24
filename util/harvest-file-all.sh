HARVEST_DIR=$G2P/harvester;
cd $HARVEST_DIR;
echo 'Launching harvesters'
harvesters=( cgi_biomarkers jax civic oncokb pmkb molecularmatch brca )
for h in "${harvesters[@]}"
do
	python harvester.py --harvesters $h --phase harvest --silos file >$h.harvest.log  &
	echo -n $h" "
	sleep 1
done
