cd ~/g2p-aggregator/harvester;
echo 'Launching harvesters'
harvesters=( cgi_biomarkers jax civic oncokb pmkb molecularmatch sage  brca )
for h in "${harvesters[@]}"
do
	python harvester.py --harvesters $h --delete_source >$h.log  &
	echo -n $h' .'
	sleep 10
done

# sleep 10
# echo -n ' jax_trials.'
# python harvester.py --harvesters jax_trials --delete_source   > jax_trials.log &

# echo -n ' molecularmatch_trials.'
# to have mm_trials simply download the data, use  ``--phases harvest --silos file` options
# python harvester.py --harvesters molecularmatch_trials --delete_source   > molecularmatch_trials.log &


echo 'All launched'
ps -ef | grep harvest | grep -v grep | grep -v Atom | awk '{print $11}' | sort
