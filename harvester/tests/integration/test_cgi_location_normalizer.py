
import json
import sys
import time
import json
sys.path.append('.')  # NOQA
from location_normalizer import normalize_feature_association
from cgi_biomarkers import convert

CGI ='{"Targeting": "", "Alteration": "FLT3::consequence::inframe_variant:572-603", "Source": "ASH 2012 (abstr 673);ASH 2012 (abstr 48)", "cDNA": [""], "Primary Tumor type": "Acute myeloid leukemia", "individual_mutation": [""], "Drug full name": "Quizartinib (Pan-TK inhibitor)", "Association": "Responsive", "Drug family": "Pan-TK inhibitor", "Biomarker": "FLT3-ITD", "Drug": "Quizartinib", "Curator": "RDientsmann", "gDNA": [""], "Drug status": "", "Gene": "FLT3", "transcript": [""], "strand": [""], "info": [""], "Assay type": "", "Alteration type": "MUT", "region": [""], "Evidence level": "Early trials", "Metastatic Tumor Type": ""}'



def test_cgi():
    evidence = json.loads(CGI)

    fa = convert(evidence).next()
    print fa
    normalize_feature_association(fa)
    for f in fa['features']:
        print f
    assert len(fa['features']) == 1
