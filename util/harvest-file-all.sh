cd ~/g2p-aggregator/harvester;
echo 'Launching harvesters'
harvesters=( cgi_biomarkers jax civic oncokb pmkb molecularmatch brca )
for h in "${harvesters[@]}"
do
	python harvester.py --harvesters $h --phase harvest --silos file >$h.harvest.log  &
	echo -n $h'\n'
	sleep 1
done
