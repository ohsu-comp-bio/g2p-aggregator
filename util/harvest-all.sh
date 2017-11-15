cd ~/g2p-aggregator/harvester;
echo 'Launching harvesters'
harvesters=( cgi_biomarkers jax civic oncokb pmkb molecularmatch sage jax_trials brca )
for h in "${harvesters[@]}"
do
	python harvester.py --harvesters $h --delete_source >$h.log  &
	echo -n $h' .'
	sleep 10
done


MM_TRIALS_START=0 MM_TRIALS_END=50000 python harvester.py --harvesters molecularmatch_trials --delete_source > MM_TRIALS.0.log &
echo -n ' molecularmatch_trials.'
sleep 20
echo -n '.'
MM_TRIALS_START=49999 MM_TRIALS_END=100000 python harvester.py --harvesters molecularmatch_trials  > MM_TRIALS.49999.log &
echo -n '.'
MM_TRIALS_START=99999 MM_TRIALS_END=150000 python harvester.py --harvesters molecularmatch_trials  > MM_TRIALS.99999.log &
echo -n '.'
MM_TRIALS_START=149999 MM_TRIALS_END=200000 python harvester.py --harvesters molecularmatch_trials  > MM_TRIALS.149999.log &
echo -n '.'
MM_TRIALS_START=199999 MM_TRIALS_END=250000 python harvester.py --harvesters molecularmatch_trials  > MM_TRIALS.199999.log &
echo -n '.'
MM_TRIALS_START=249999 MM_TRIALS_END=300000 python harvester.py --harvesters molecularmatch_trials  > MM_TRIALS.249999.log &

echo 'All launched'
ps -ef | grep harvest | grep -v grep | grep -v Atom | awk '{print $11}' | sort
