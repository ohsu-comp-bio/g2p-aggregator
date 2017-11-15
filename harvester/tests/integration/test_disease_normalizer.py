import sys
sys.path.append('.')  # NOQA

from disease_normalizer import normalize
import requests
import requests_cache
# cache responses
requests_cache.install_cache('harvester')


def test_Gastrointestinal_Stromal_Tumor():
    diseases = normalize("Gastrointestinal Stromal Tumor")
    assert diseases[0]['ontology_term'] == 'DOID:9253'
    assert diseases[0]['label'] == 'gastrointestinal stromal tumor'


def test_triple_receptor_negative_breast_cancer():
    diseases = normalize("triple-receptor negative breast cancer")
    assert diseases[0]['ontology_term'] == 'DOID:0060081'
    assert diseases[0]['label'] == 'triple-receptor negative breast cancer'


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


def test_CML():
    diseases = normalize("CML")
    assert diseases[0]['ontology_term'] == 'DOID:8552'
    assert diseases[0]['label'] == 'chronic myeloid leukemia'


def test_Her2_receptor_positive_breast_cancer():
    diseases = normalize("Her2-receptor positive breast cancer")
    assert diseases[0]['ontology_term'] == 'DOID:0060079'
    assert diseases[0]['label'] == 'Her2-receptor positive breast cancer'


def test_comma_separator():
    diseases = normalize("CML,stomach cancer")
    assert len(diseases) == 2


def test_semicolon_separator():
    diseases = normalize("CML;stomach cancer")
    assert len(diseases) == 2


def test_LUAD_TH():
    diseases = normalize("LUAD;TH")
    assert len(diseases) == 2


def test_BRCA_BOCA():
    diseases = normalize("BRCA;BOCA")
    assert len(diseases) == 2


def test_Advanced_Solid_Tumor():
    diseases = normalize("Advanced Solid Tumor")
    assert diseases[0]['ontology_term'] == 'DOID:162'


def test_Astrocytoma_Anaplastic():
    diseases = normalize("Astrocytoma, Anaplastic")
    assert diseases[0]['ontology_term'] == 'DOID:3069'


def test_ovary_adenocarcinoma():
    diseases = normalize('ovary adenocarcinoma')
    assert diseases[0]['ontology_term'] == 'DOID:3713'


def test_Malignant_Lymphoma():
    diseases = normalize('Malignant Lymphoma')
    assert diseases[0]['ontology_term'] == 'DOID:0060058'
    print diseases


def test_Glioma():
    diseases = normalize('Glioma')
    assert diseases[0]['ontology_term'] == 'HP:0009733'
    assert diseases[0]['family'] == 'Neuroepithelial neoplasm'


def test_Heart_failure():
    diseases = normalize('Heart failure')
    assert diseases[0]['ontology_term'] == 'SYMP:0000292'
    assert diseases[0]['family'] == 'cardiovascular system symptom'


def test_HF():
    diseases = normalize('HF - Heart failure')
    assert diseases[0]['ontology_term'] == 'SYMP:0000292'
    assert diseases[0]['family'] == 'cardiovascular system symptom'


def test_Lung():
    diseases = normalize('Lung')
    assert diseases[0]['ontology_term'] == 'DOID:1324'
    assert diseases[0]['family'] == 'respiratory system cancer'


def test_HIV():
    diseases = normalize('HIV - Human immunodeficiency virus infection')
    assert diseases[0]['ontology_term'] == 'DOID:526'
    assert diseases[0]['family'] == 'human immunodeficiency virus infectious disease'


def test_Plasmacytic_myeloma():
    diseases = normalize('Plasmacytic myeloma')
    print diseases
    assert diseases[0]['ontology_term'] == 'DOID:9538'
    assert diseases[0]['family'] == 'hematologic cancer'
#
#
# multiple myeloma
#
# multiple myeloma
