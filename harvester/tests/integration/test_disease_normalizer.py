import sys
sys.path.append('.')  # NOQA
import logging
logging.basicConfig(level=logging.DEBUG)

from disease_normalizer import normalize
import requests
import requests_cache
# cache responses
requests_cache.install_cache('harvester')


def test_comma():
    term = "Non-small cell lung cancer, positive for epidermal growth factor receptor expression"
    diseases = normalize(term)
    print diseases
    term = "Non-small cell lung cancer"
    diseases = normalize(term)
    print diseases

def test_Gastrointestinal_Stromal_Tumor():
    diseases = normalize("Gastrointestinal Stromal Tumor")
    assert diseases[0]['ontology_term'] == 'DOID:9253'
    assert diseases[0]['label'] == 'gastrointestinal stromal tumor'
    assert diseases[0]['source']


def test_triple_receptor_negative_breast_cancer():
    diseases = normalize("triple-receptor negative breast cancer")
    assert diseases[0]['ontology_term'] == 'DOID:0060081'
    assert diseases[0]['label'] == 'triple-receptor negative breast cancer'
    assert diseases[0]['source']


def test_Advanced_Solid_Tumor():
    diseases = normalize("Advanced Solid Tumor")
    assert len(diseases) == 0
    # see https://ckb.jax.org/diseaseOntology/show?doId=10000003
    """ An abnormal mass of tissue that usually does not contain cysts
    or liquid areas. Different types of solid tumors are named for the type
    of cells that form them. Examples of solid tumors are sarcomas,
    carcinomas, and lymphomas).
    Source The Jackson Laboratory (a custom term added that does not corresond
    to an existing term in the disease ontology)
     """


def test_stomach_cancer():
    diseases = normalize("stomach cancer")
    assert diseases[0]['ontology_term'] == 'DOID:10534'
    assert diseases[0]['label'] == 'stomach cancer'
    assert diseases[0]['source']


def test_CML():
    diseases = normalize("CML")
    assert diseases[0]['ontology_term'] == 'DOID:8552'
    assert diseases[0]['label'] == 'chronic myeloid leukemia'
    assert diseases[0]['source']


def test_Her2_receptor_positive_breast_cancer():
    diseases = normalize("Her2-receptor positive breast cancer")
    assert diseases[0]['ontology_term'] == 'DOID:0060079'
    assert diseases[0]['label'] == 'Her2-receptor positive breast cancer'
    assert diseases[0]['source']


def test_comma_separator():
    diseases = normalize("CML,stomach cancer")
    assert len(diseases) == 2
    assert diseases[0]['source']
    assert diseases[1]['source']


def test_semicolon_separator():
    diseases = normalize("CML;stomach cancer")
    assert len(diseases) == 2
    assert diseases[0]['source']
    assert diseases[1]['source']


def test_LUAD():
    diseases = normalize("LUAD")
    assert len(diseases) == 1
    assert diseases[0]['ontology_term'] == 'DOID:3910'


def test_LUAD_TH():
    diseases = normalize("LUAD;TH")
    assert len(diseases) == 2
    assert diseases[0]['ontology_term'] == 'DOID:3910'
    assert diseases[1]['ontology_term'] == 'DOID:1781'
    print diseases


def test_BRCA_BOCA():
    diseases = normalize("BRCA;BOCA")
    assert len(diseases) == 2
    assert diseases[0]['source']
    assert diseases[1]['source']


def test_Advanced_Solid_Tumor():
    diseases = normalize("Advanced Solid Tumor")
    assert diseases[0]['ontology_term'] == 'DOID:162'
    assert diseases[0]['source']


def test_Astrocytoma_Anaplastic():
    diseases = normalize("Astrocytoma, Anaplastic")
    assert diseases[0]['ontology_term'] == 'DOID:3069'
    assert diseases[0]['source']


def test_ovary_adenocarcinoma():
    diseases = normalize('ovary adenocarcinoma')
    assert diseases[0]['ontology_term'] == 'DOID:3713'
    assert diseases[0]['source']


def test_Malignant_Lymphoma():
    diseases = normalize('Malignant Lymphoma')
    assert diseases[0]['ontology_term'] == 'DOID:0060058'
    assert diseases[0]['source']


def test_Glioma():
    diseases = normalize('Glioma')
    assert diseases[0]['ontology_term'] == 'HP:0009733'
    assert diseases[0]['family'] == 'Neuroepithelial neoplasm'
    assert diseases[0]['source']


def test_Heart_failure():
    diseases = normalize('Heart failure')
    assert diseases[0]['ontology_term'] == 'SYMP:0000292'
    assert diseases[0]['family'] == 'cardiovascular system symptom'
    assert diseases[0]['source']


def test_HF():
    diseases = normalize('HF - Heart failure')
    assert diseases[0]['ontology_term'] == 'SYMP:0000292'
    assert diseases[0]['family'] == 'cardiovascular system symptom'
    assert diseases[0]['source']


def test_Lung():
    diseases = normalize('Lung')
    assert diseases[0]['ontology_term'] == 'DOID:1324'
    assert diseases[0]['family'] == 'respiratory system cancer'
    assert diseases[0]['source']


def test_HIV():
    diseases = normalize('HIV - Human immunodeficiency virus infection')
    assert diseases[0]['ontology_term'] == 'DOID:526'
    assert diseases[0]['family'] == 'human immunodeficiency virus infectious disease'  # NOQA
    assert diseases[0]['source']


def test_Plasmacytic_myeloma():
    diseases = normalize('Plasmacytic myeloma')
    assert diseases[0]['ontology_term'] == 'DOID:9538'
    assert diseases[0]['family'] == 'hematologic cancer'
    assert diseases[0]['source']


def test_Myeloproliferative_disorder():
    diseases = normalize('Myeloproliferative disorder')
    assert diseases[0]['ontology_term'] == 'DOID:2226'
    assert diseases[0]['family'] == 'hematologic cancer'
    assert diseases[0]['source']


def test_Diffuse_malignant_lymphoma_histiocytic():
    diseases = normalize('Diffuse malignant lymphoma - histiocytic')
    assert diseases[0]['ontology_term'] == 'DOID:8675'
    assert diseases[0]['family'] == 'immune system cancer'
    assert diseases[0]['source']


def test_Follicular_non_Hodgkin_lymphoma():
    diseases = normalize('Follicular non-Hodgkin lymphoma')
    assert diseases[0]['ontology_term'] == 'DOID:0060060'
    assert diseases[0]['family'] == 'hematologic cancer'
    assert diseases[0]['source']


def test_Merkel_cell_carcinoma():
    diseases = normalize('Merkel cell carcinoma')
    assert diseases[0]['ontology_term'] == 'DOID:3965'
    assert diseases[0]['family'] == 'skin cancer'
    assert diseases[0]['source']


def test_Cancer_of_intraabdominal_organ():
    diseases = normalize('Cancer of intraabdominal organ')
    assert diseases[0]['ontology_term'] == 'SNOMEDCT:448882009'
    assert diseases[0]['family'] == 'Malignant neoplasm of abdomen'
    assert diseases[0]['source']


def test_Primary_malignant_neoplasm_of_retroperitoneum():
    diseases = normalize('Primary malignant neoplasm of retroperitoneum')
    assert diseases[0]['ontology_term'] == 'SNOMEDCT:94092006'
    assert diseases[0]['family'] == 'Primary malignant neoplasm of trunk'
    assert diseases[0]['source']


def test_Malignant_tumour_of_urinary_tract_proper():
    diseases = normalize('Malignant tumour of urinary tract proper')
    print diseases
    assert diseases[0]['ontology_term'] == 'RCD:X78it'
    assert diseases[0]['family'] == 'Malignant tumour'
    assert diseases[0]['source']


def test_Cancer_of_digestive_system():
    diseases = normalize('Cancer of digestive system')
    assert diseases[0]['ontology_term'] == 'DOID:8377'
    assert diseases[0]['source']


def test_misc_tcga_codes():
    codes = ['COADREAD', 'DLBC', 'KIRC', 'KIRP', 'LGG', 'LIHC', 'MESO', 'PCPG',
             'SKCM', 'TGCT']
    for code in codes:
        diseases = normalize(code)
        assert len(diseases) > 0
        print code, "-->", diseases


def test_PCPG():
    diseases = normalize('PCPG')
    assert len(diseases) > 0
    print diseases
