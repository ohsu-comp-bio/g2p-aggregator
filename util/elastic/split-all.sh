python get_index.py --index associations | tee  \
  >(grep '"source":"cgi"' > cgi.json ) \
  >(grep '"source":"jax"' > jax.json ) \
  >(grep '"source":"oncokb"' > oncokb.json ) \
  >(grep '"source":"pmkb"' > pmkb.json ) \
  >(grep '"source":"molecularmatch"' > molecularmatch.json ) \
  >(grep '"source":"sage"' > sage.json ) \
  >(grep '"source":"jax_trials"' > jax_trials.json ) \
  >(grep '"source":"molecularmatch_trials"' > molecularmatch_trials.json ) \
  >(grep '"source":"brca"' > brca.json ) \
  >(grep '"source":"civic"' > civic.json ) \
  >(grep '"source":"litvar"' > litvar.json ) \
> all.json
