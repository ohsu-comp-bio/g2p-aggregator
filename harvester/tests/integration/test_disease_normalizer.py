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
    print 'diseases', diseases


def test_Astrocytoma_Anaplastic():
    diseases = normalize("Astrocytoma, Anaplastic")
    print 'diseases', diseases
