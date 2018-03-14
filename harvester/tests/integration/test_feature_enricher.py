
import json
import sys
import time
sys.path.append('.')  # NOQA
from feature_enricher import enrich


def test_gene_enrichment():
    features = enrich({'name': 'BRCA1'}, {})
    assert features[0] == {'end': 41277500, 'name': 'BRCA1', 'start': 41196312, 'referenceName': 'GRCh37', 'chromosome': '17', 'description': 'BRCA1', 'provenance': ['http://mygene.info/v3/query?q=BRCA1&fields=genomic_pos_hg19'], 'provenance_rule': 'gene_only' }


def test_gene_enrichment_JAK():
    features = enrich({'name': 'JAK'}, {})
    assert features[0] == {'end': 27418537, 'name': 'JAK', 'start': 27400537, 'referenceName': 'GRCh37', 'chromosome': '17', 'description': 'JAK', 'provenance': ['http://mygene.info/v3/query?q=JAK&fields=genomic_pos_hg19'], 'provenance_rule': 'gene_only'}


def test_feature_enrichment():
    features = enrich({'name': 'BRCA1 V600E'}, {})
    assert features[0] == {'end': 41245877, 'name': 'BRCA1 V600E', 'start': 41245877, 'biomarker_type': 'nonsense', 'referenceName': 'GRCh37', 'alt': u'A', 'ref': u'T', 'chromosome': '17', 'description': 'BRCA1 V600E', 'provenance': ['http://myvariant.info/v1/query?q=BRCA1 V600E'], 'provenance_rule': 'default_feature'}


def test_feature_enrichment_ALK_D1203N():
    features = enrich({'name': "ALK D1203N "}, {})
    assert features[0] == {'end': 29940443, 'name': 'ALK D1203N ', 'start': 29940443, 'referenceName': 'GRCh37', 'alt': u'T', 'ref': u'C', 'chromosome': '2', 'description': 'ALK D1203N ', 'provenance': ['http://myvariant.info/v1/query?q=ALK D1203N '], 'provenance_rule': 'default_feature'}


def test_feature_enrichment_AR_amplification():
    features = enrich({'name': 'AR amplification'}, {})
    assert features[0] == {'provenance_rule': 'is_amplification', 'end': 66950461, 'name': 'AR amplification', 'provenance': ['http://mygene.info/v3/query?q=AR&fields=genomic_pos_hg19'], 'start': 66764465, 'referenceName': 'GRCh37', 'chromosome': 'X', 'description': 'AR amplification'}


def test_feature_enrichment_Exon_19_deletion_insertion():
    oncokb = {"clinical": {"level": "1", "Isoform": "ENST00000275493", "variant": {"variantResidues": None, "proteinStart": 729, "name": "Exon 19 deletion/insertion", "proteinEnd": 761, "refResidues": None, "alteration": "729_761indel", "consequence": {"term": "NA", "description": "NA", "isGenerallyTruncating": False}, "gene": {"oncogene": True, "name": "epidermal growth factor receptor", "hugoSymbol": "EGFR", "entrezGeneId": 1956, "tsg": False, "geneAliases": ["PIG61", "ERBB1", "mENA", "ERBB", "HER1", "NISBD2"], "curatedRefSeq": "NM_005228.3", "curatedIsoform": "ENST00000275493"}}, "Entrez Gene ID": 1956, "drugAbstracts": [{"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/15638953"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/22452895"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/25589191"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/23816960"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/14570950"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/22285168"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/20022809"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/19692680"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/21670455"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/18408761"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/22370314"}, {"text": "", "link": "http://www.ncbi.nlm.nih.gov/pubmed/20573926"}], "cancerType": "Non-Small Cell Lung Cancer", "level_label": "FDA-approved biomarker and drug in this indication", "drug": "Afatinib, Erlotinib, Gefitinib", "RefSeq": "NM_005228.3", "gene": "EGFR", "drugPmids": "15638953, 22452895, 25589191, 23816960, 14570950, 22285168, 20022809, 19692680, 21670455, 18408761, 22370314, 20573926"}}
    features = enrich({'name': 'Exon 19 deletion/insertion'}, {'source': 'oncokb', 'oncokb': oncokb})
    assert features == [{'provenance_rule': 'is_oncokb_ensemble', 'end': 55279321, 'name': 'Exon 19 deletion/insertion', 'provenance': ['http://grch37.rest.ensembl.org/lookup/id/ENST00000275493?expand=1'], 'start': 55086794, 'referenceName': 'GRCh37', 'chromosome': '7', 'description': 'Exon 19 deletion/insertion'}]
