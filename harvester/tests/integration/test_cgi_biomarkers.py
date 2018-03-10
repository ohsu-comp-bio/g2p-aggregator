
import json
import sys
import time
sys.path.append('.')  # NOQA
from jax import convert as jax_convert
from cgi_biomarkers import convert as cgi_convert

from location_normalizer import normalize_feature_association
from harvester import normalize

from attrdict import AttrDict


def test_convert():
    evidence = {"responseType": "decreased response", "efficacyEvidence": "In a preclinical study, transformed cells expressing EML4-ALK, ALK D1203N, and ALK E1210K demonstrated a decreased response to treatment with Zykadia (ceritinib) in culture (PMID: 27432227). ", "molecularProfile": {"profileName": "EML4-ALK ALK D1203N ALK E1210K", "id": 26388}, "evidenceType": "Actionable", "indication": {"source": "JAX", "id": 10000003, "name": "Advanced Solid Tumor"}, "references": [{"url": "http://www.ncbi.nlm.nih.gov/pubmed/27432227", "id": 6706, "pubMedId": 27432227, "title": "Molecular Mechanisms of Resistance to First- and Second-Generation ALK Inhibitors in ALK-Rearranged Lung Cancer."}], "approvalStatus": "Preclinical - Cell culture", "therapy": {"id": 789, "therapyName": "Ceritinib"}, "id": 8656}

    jax_evidence = AttrDict({'gene': 'ALK', 'jax_id': 6706, 'evidence': evidence})

    for fa in jax_convert(jax_evidence):
        pass
    assert len(fa['features']) > 1
    print fa
    normalize_feature_association(fa)
    print fa


def test_cgi():
    evidence = {"Targeting": "", "Biomarker": "STK11 oncogenic mutation", "Source": "PMID:19165201", "cDNA": [""], "Primary Tumor type": "Lung adenocarcinoma", "individual_mutation": [""], "Drug full name": "MEK inhibitors", "Association": "Responsive", "Drug family": "[MEK inhibitor]", "Curator": "RDientsmann", "Drug": "[]", "Alteration": "STK11:.", "gDNA": [""], "Drug status": "", "Gene": "STK11", "transcript": [""], "strand": [""], "info": [""], "Assay type": "", "Alteration type": "MUT", "region": [""], "Evidence level": "Pre-clinical", "Metastatic Tumor Type": ""}

    for fa in cgi_convert(evidence):
        print fa['features']
        assert len(fa['features']) == 1
        normalize(fa)
        assert len(fa['features']) == 8
        # print len(fa['features'])
        #print fa['features']
