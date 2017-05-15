#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import argparse
import time
import json
import os
sys.path.append(os.getcwd() + '/tests/integration')  # NOQA

from google.protobuf import json_format
from ga4gh import genotype_phenotype_pb2 as g2p
from ga4gh import sequence_annotations_pb2 as annotations
from ohsu import g2p_pb2 as evidence

CIVIC_TEST_MESSAGE = """
{"source": "civic", "gene": "CDKN2A", "feature": {"entrez_id": 1029, "end": 21974865, "name": "p16 EXPRESSION", "start": 21968055, "referenceName": "GRCh37", "geneSymbol": "CDKN2A", "chromosome": "9"}, "association": {"drug_labels": "", "description": "Patients from three studies (RTOG 0129, 0234, and 0522; 85, 95 and 142 patients, respectively) were retrospectively analyzed for p16 (CDKN2A) expression (IHC) and HPV-high risk status (ISH). p16 expression in non-oropharyngeal HNSSC was also prognostic and associated with a better outcome. However, p16-positive oropharyngeal HNSSC still had better PFS and OS than p16-positive non-oropharyngeal HNSSC.", "publication_url": ["http://www.ncbi.nlm.nih.gov/pubmed/25267748"], "evidence": [{"info": {"publications": ["http://www.ncbi.nlm.nih.gov/pubmed/25267748"]}, "evidenceType": {"sourceName": "CIVIC", "id": "804"}, "description": "Better Outcome"}], "environmentalContexts": [], "evidence_label": ["Better Outcome"], "phenotype": {"description": "Head And Neck Squamous Cell Carcinoma", "id": "http://www.disease-ontology.org/?id=DOID:5520"}}, "civic": {"evidence_items": [{"status": "accepted", "rating": 3, "drug_interaction_type": null, "description": "Patients from three studies (RTOG 0129, 0234, and 0522; 85, 95 and 142 patients, respectively) were retrospectively analyzed for p16 (CDKN2A) expression (IHC) and HPV-high risk status (ISH). p16 expression in non-oropharyngeal HNSSC was also prognostic and associated with a better outcome. However, p16-positive oropharyngeal HNSSC still had better PFS and OS than p16-positive non-oropharyngeal HNSSC.", "open_change_count": 0, "evidence_type": "Prognostic", "drugs": [], "variant_origin": "Somatic Mutation", "disease": {"doid": "5520", "url": "http://www.disease-ontology.org/?id=DOID:5520", "display_name": "Head And Neck Squamous Cell Carcinoma", "id": 37, "name": "Head And Neck Squamous Cell Carcinoma"}, "source": {"status": "fully curated", "open_access": true, "name": "p16 protein expression and human papillomavirus status as prognostic biomarkers of nonoropharyngeal head and neck squamous cell carcinoma.", "journal": "J. Clin. Oncol.", "citation": "Chung et al., 2014, J. Clin. Oncol.", "pmc_id": "PMC4251957", "full_journal_title": "Journal of clinical oncology : official journal of the American Society of Clinical Oncology", "source_url": "http://www.ncbi.nlm.nih.gov/pubmed/25267748", "pubmed_id": "25267748", "publication_date": {"month": 12, "day": 10, "year": 2014}, "id": 538}, "evidence_direction": "Supports", "variant_id": 272, "clinical_significance": "Better Outcome", "evidence_level": "B", "type": "evidence", "id": 804, "name": "EID804"}], "entrez_name": "CDKN2A", "variant_types": [{"display_name": "N/A", "description": "No suitable Sequence Ontology term exists.", "url": "http://www.sequenceontology.org/browser/current_svn/term/N/A", "so_id": "N/A", "id": 183, "name": "N/A"}], "description": "CDKN2A (p16) expression is a surrogate marker of HPV infection in oropharyngeal squamous cell carcinoma. CDKN2A and p53 are inactivated through HPV proteins E6 and E7 and therefore not altered in expression level in HPV-associated carcinomas. However, there is no perfect overlap between p16 expression and HPV status with some 10-12.5% of HPV-negative tumors expressing p16. (Seiwert, T JCO, 2014). p16 positivity is a well-established positive prognostic factor in squamous cell cancer of the head and neck in the primary and, as increasing evidence suggests, recurrent/metastatic disease settings. Predictive information from HPV status have not been established to date. A lack of benefit from EGFR-inhibitors has been proposed by some studies. Other studies were not able to reproduce this finding.", "lifecycle_actions": {"last_modified": {"timestamp": "2016-09-10T01:45:30.838Z", "order": 0, "user": {"username": "kkrysiak", "area_of_expertise": "Research Scientist", "twitter_handle": "", "display_name": "kkrysiak", "name": "Kilannin Krysiak", "bio": "Dr. Krysiak is an Instructor at the McDonnell Genome Institute at Washington University School of Medicine where she is involved in the comprehensive genomic analysis of cancer patient cohorts and “n-of-1” studies. She received her PhD in Molecular Genetics and Genomics at Washington University in St. Louis where she focused on the genetics of myelodysplastic syndrome through advanced flow cytometry techniques, primary cell culture and mouse models. She is a founding member of the CIViC team, helping to define the CIViC data model, and a leading content curator and feature development consultant.", "url": "", "created_at": "2015-02-26T04:14:20.953Z", "avatars": {"x32": "https://secure.gravatar.com/avatar/17180f9afc9f7f04fff97197c1ee5cb6.png?d=identicon&r=pg&s=32", "x14": "https://secure.gravatar.com/avatar/17180f9afc9f7f04fff97197c1ee5cb6.png?d=identicon&r=pg&s=14", "x64": "https://secure.gravatar.com/avatar/17180f9afc9f7f04fff97197c1ee5cb6.png?d=identicon&r=pg&s=64", "x128": "https://secure.gravatar.com/avatar/17180f9afc9f7f04fff97197c1ee5cb6.png?d=identicon&r=pg&s=128"}, "orcid": "0000-0002-6299-9230", "accepted_license": null, "affiliation": null, "avatar_url": "https://secure.gravatar.com/avatar/17180f9afc9f7f04fff97197c1ee5cb6.png?d=identicon&r=pg&s=32", "role": "admin", "facebook_profile": "", "linkedin_profile": "kilannin-krysiak-69047819", "organization": null, "last_seen_at": "2017-04-17T20:57:56.001Z", "featured_expert": true, "id": 6, "signup_complete": null}}, "last_reviewed": {"timestamp": "2016-09-13T20:26:46.536Z", "order": 1, "user": {"username": "MalachiGriffith", "area_of_expertise": "Research Scientist", "twitter_handle": "malachigriffith", "display_name": "MalachiGriffith", "name": "Malachi Griffith", "bio": "Dr. Griffith is an Assistant Professor of Medicine and Assistant Director of the McDonnell Genome Institute at Washington University School of Medicine. Dr Griffith has extensive experience in the fields of genomics, bioinformatics, data mining, and cancer research. His research is focused on improving the understanding of cancer biology and the development of personalized medicine strategies for cancer using genomics and informatics technologies. The Griffith lab develops bioinformatics and statistical methods for the analysis of high throughput sequence data and identification of biomarkers for diagnostic, prognostic and drug response prediction. The Griffith lab uses CIViC to interpret variants identified in cases examined by the WASHU Genomics Tumor Board. He is a co-creator of the CIViC resource.", "url": "http://genome.wustl.edu/people/individual/malachi-griffith/", "created_at": "2015-02-26T22:25:34.692Z", "avatars": {"x32": "https://secure.gravatar.com/avatar/a4d9fc3b05d58cf3d3ba51dc30bb61d6.png?d=identicon&r=pg&s=32", "x14": "https://secure.gravatar.com/avatar/a4d9fc3b05d58cf3d3ba51dc30bb61d6.png?d=identicon&r=pg&s=14", "x64": "https://secure.gravatar.com/avatar/a4d9fc3b05d58cf3d3ba51dc30bb61d6.png?d=identicon&r=pg&s=64", "x128": "https://secure.gravatar.com/avatar/a4d9fc3b05d58cf3d3ba51dc30bb61d6.png?d=identicon&r=pg&s=128"}, "orcid": "0000-0002-6388-446X", "accepted_license": null, "affiliation": null, "avatar_url": "https://secure.gravatar.com/avatar/a4d9fc3b05d58cf3d3ba51dc30bb61d6.png?d=identicon&r=pg&s=32", "role": "admin", "facebook_profile": null, "linkedin_profile": "malachigriffith", "organization": null, "last_seen_at": "2017-04-13T21:23:36.160Z", "featured_expert": true, "id": 15, "signup_complete": null}}}, "gene_id": 14, "name": "p16 EXPRESSION", "variant_groups": [], "sources": [{"status": "fully curated", "open_access": null, "name": "Ties that bind: p16 as a prognostic biomarker and the need for high-accuracy human papillomavirus testing.", "journal": "J. Clin. Oncol.", "citation": "Seiwert, 2014, J. Clin. Oncol.", "pmc_id": null, "full_journal_title": "Journal of clinical oncology : official journal of the American Society of Clinical Oncology", "source_url": "http://www.ncbi.nlm.nih.gov/pubmed/25366683", "pubmed_id": "25366683", "publication_date": {"year": 2014, "day": 10, "month": 12}, "id": 537}], "entrez_id": 1029, "variant_aliases": [], "hgvs_expressions": [], "errors": {}, "coordinates": {"chromosome2": null, "reference_bases": null, "start2": null, "variant_bases": null, "stop": 21974865, "stop2": null, "representative_transcript2": null, "start": 21968055, "representative_transcript": "ENST00000498124.1", "ensembl_version": 75, "chromosome": "9", "reference_build": "GRCh37"}, "type": "variant", "id": 272, "statuses": {"has_pending_fields": false, "has_pending_evidence": false}, "clinvar_entries": []}}
"""  # NOQA

JAX_TEST_MESSAGE = """
{"source": "jax", "gene": "CDKN2A", "feature": {"geneSymbol": "CDKN2A", "name": "CDKN2A loss"}, "association": {"drug_labels": "GSK461364 + PD0332991", "description": "In a preclinical study, Ibrance (palbociclib) antagonized the efficacy of GSK461364 in pancreatic cancer cells with CDKN2A loss in culture (PMID: 25156567).", "publication_url": "http://www.ncbi.nlm.nih.gov/pubmed/25156567", "evidence": [{"info": {"publications": [["http://www.ncbi.nlm.nih.gov/pubmed/25156567"]]}, "evidenceType": {"sourceName": "jax"}, "description": "decreased response"}], "environmentalContexts": [{"description": "GSK461364 + PD0332991"}], "evidence_label": "decreased response", "phenotype": {"description": "pancreatic cancer"}}, "jax": {"approval_status": "Preclinical", "evidence_type": "Actionable", "indication_tumor_type": "pancreatic cancer", "references": ["25156567"], "response_type": "decreased response", "efficacy_evidence": "In a preclinical study, Ibrance (palbociclib) antagonized the efficacy of GSK461364 in pancreatic cancer cells with CDKN2A loss in culture (PMID: 25156567).", "molecular_profile": "CDKN2A loss", "therapy_name": "GSK461364 + PD0332991"}}
"""  # NOQA

ONCOKB_TEST_MESSAGE = """
{"source": "oncokb", "gene": "CDKN2A", "oncokb": {"clinical": {"level": "4", "drugPmids": ["26380006"], "variant": {"variantResidues": null, "proteinStart": -1, "name": "Oncogenic Mutations", "proteinEnd": 100000, "refResidues": null, "alteration": "Oncogenic Mutations", "consequence": {"term": "NA", "description": "NA", "isGenerallyTruncating": false}, "gene": {"oncogene": false, "name": "cyclin dependent kinase inhibitor 2A", "hugoSymbol": "CDKN2A", "entrezGeneId": 1029, "tsg": true, "geneAliases": ["P16INK4A", "MTS1", "TP16", "P16INK4", "INK4", "P14ARF", "P19ARF", "CDK4I", "MLM", "CMM2", "P14", "MTS-1", "P16", "ARF", "P19", "INK4A", "P16-INK4A", "CDKN2"], "curatedRefSeq": "NM_000077.4", "curatedIsoform": "ENST00000304494"}}, "drug": ["Palbociclib"], "cancerType": {"code": null, "name": null, "parent": null, "level": null, "color": null, "deprecated": false, "children": {}, "links": null, "mainType": {"id": 32, "name": "Esophagogastric Cancer"}, "NCI": null, "tissue": null, "UMLS": null, "id": null, "history": []}, "drugAbstracts": [], "level_label": "Preclinical evidence associates this biomarker to drug response, where the biomarker and drug are NOT FDA-approved or NCCN compendium-listed"}}, "feature": {"geneSymbol": "CDKN2A", "entrez_id": 1029, "name": "Oncogenic Mutations"}, "association": {"drug_labels": "Palbociclib", "description": "Preclinical evidence associates this biomarker to drug response, where the biomarker and drug are NOT FDA-approved or NCCN compendium-listed", "publication_url": "http://www.ncbi.nlm.nih.gov/pubmed/26380006", "evidence": [{"info": {"publications": [[]]}, "evidenceType": {"sourceName": "oncokb", "id": "CDKN2A-32"}, "description": "Preclinical evidence associates this biomarker to drug response, where the biomarker and drug are NOT FDA-approved or NCCN compendium-listed"}], "environmentalContexts": [{"description": "Palbociclib"}], "evidence_label": "Preclinical evidence associates this biomarker to drug response, where the biomarker and drug are NOT FDA-approved or NCCN compendium-listed", "phenotype": {"description": "Esophagogastric Cancer", "id": "32"}}}
"""  # NOQA

MOLECULAR_MATCH_TEST_MESSAGE = """
{"source": "molecularmatch", "gene": "DDR2", "feature": {"geneSymbol": "DDR2", "name": "DDR2 G505S"}, "association": {"drug_labels": "Dasatinib", "description": "DDR2 G505S confers sensitivity to Dasatinib in patients with Neoplasm of lung", "publication_url": "https://www.ncbi.nlm.nih.gov/pubmed/22328973", "evidence": [{"info": {"publications": ["https://www.ncbi.nlm.nih.gov/pubmed/22328973"]}, "evidenceType": {"sourceName": "molecularmatch"}, "description": "DDR2 G505S confers sensitivity to Dasatinib in patients with Neoplasm of lung"}], "environmentalContexts": [{"description": "Dasatinib"}], "evidence_label": "supports", "phenotype": {"description": "Neoplasm of lung"}}, "molecularmatch": {"customer": "MolecularMatch", "regulatoryBody": "FDA", "direction": "supports", "tier": "3", "sources": [{"preclinicalType": "cell line", "name": "PUBMED", "suppress": false, "link": "https://www.ncbi.nlm.nih.gov/pubmed/22328973", "year": "", "type": "preclinical", "id": "22328973"}], "mboost": 0, "autoGenerateNarrative": true, "biomarkerClass": "predictive", "ast": {"operator": "&&", "right": {"raw": "\\"DDR2 G505S\\"", "type": "Literal", "value": "DDR2 G505S"}, "type": "LogicalExpression", "left": {"raw": "\\"Neoplasm of lung\\"", "type": "Literal", "value": "Neoplasm of lung"}}, "mutations": [{"hotspots": [], "name": "DDR2 G505S", "exons": ["14"], "exons_B": [], "introns": [], "sources": ["CIViC", "ClinVar", "DoCM"], "genomicLocations_B": [], "domains": [], "genomicLocations": ["1_162741822_162741822_G_A"], "transcripts": ["NM_001014796.1", "NM_006182.2", "NM_001014796.1", "NM_006182.2"], "introns_B": []}], "narrative": "DDR2 G505S confers sensitivity to Dasatinib in patients with Neoplasm of lung", "regulatoryBodyApproved": false, "version": 1, "therapeuticContext": [{"facet": "DRUG", "suppress": false, "valid": true, "name": "Dasatinib"}], "clinicalSignificance": "sensitive", "criteriaUnmet": [{"priority": 1, "term": "Neoplasm of lung", "suppress": false, "filterType": "include", "primary": true, "custom": true, "facet": "CONDITION", "valid": true, "compositeKey": "Neoplasm of lungCONDITIONinclude"}, {"priority": 1, "term": "DDR2 G505S", "suppress": false, "filterType": "include", "compositeKey": "DDR2 G505SMUTATIONinclude", "custom": true, "facet": "MUTATION", "valid": true}], "includeMutation1": ["DDR2 G505S"], "includeCondition1": ["Neoplasm of lung"], "expression": "\\"Neoplasm of lung\\" && \\"DDR2 G505S\\"", "id": "c8280f2a-66fe-4db1-a80b-d4a7e7f6bdb2", "tags": [{"priority": 1, "term": "Neoplasm of lung", "suppress": false, "filterType": "include", "primary": true, "custom": true, "facet": "CONDITION", "valid": true, "compositeKey": "Neoplasm of lungCONDITIONinclude"}, {"priority": 1, "term": "DDR2 G505S", "suppress": false, "filterType": "include", "compositeKey": "DDR2 G505SMUTATIONinclude", "custom": true, "facet": "MUTATION", "valid": true}]}}
"""  # NOQA

CGI_TEST_MESSAGE = """
{"cgi": {"Primary Tumor type": "G;CANCER", "Drug family": "[CDK4/6 inhibitor]", "Alteration type": "MUT", "Targeting": "", "Assay type": "", "Evidence level": "Pre-clinical", "Biomarker": "CDKN2A oncogenic mutation", "Drug": "[]", "Alteration": "CDKN2A:.", "Source": "PMID:22471707;PMID:22586120;PMID:22711607", "Curator": "RDientsmann", "Comments": "", "Drug status": "", "Drug full name": "CDK4/6 inhibitors", "TCGI included": true, "Curation date": "", "Gene": "CDKN2A", "Metastatic Tumor Type": "", "Association": "Responsive"}, "source": "cgi", "gene": "CDKN2A", "feature": {"geneSymbol": "CDKN2A", "name": "CDKN2A oncogenic mutation", "description": "CDKN2A:."}, "association": {"drug_labels": "CDK4/6 inhibitors", "description": "CDKN2A CDK4/6 inhibitors Responsive", "publication_url": "http://www.ncbi.nlm.nih.gov/pubmed/22471707", "evidence": [{"info": {"publications": ["http://www.ncbi.nlm.nih.gov/pubmed/22471707", "http://www.ncbi.nlm.nih.gov/pubmed/22586120", "http://www.ncbi.nlm.nih.gov/pubmed/22711607"]}, "evidenceType": {"sourceName": "cgi"}, "description": "Responsive"}], "environmentalContexts": [{"description": "CDK4/6 inhibitors"}], "evidence_label": "Responsive Pre-clinical", "phenotype": {"description": "G;CANCER"}}}
"""  # NOQA

PMKB_TEST_MESSAGE = """
{"tags": [], "feature": {"end": "133748283", "name": "ABL1 T315I", "start": "133748283", "referenceName": "GRCh37/hg19", "geneSymbol": "ABL1", "attributes": {"amino_acid_change": {"string_value": "T315I"}, "exons": {"string_value": "6"}, "url": {"string_value": "https://pmkb.weill.cornell.edu/genes/38/variants/101"}, "is_germline_somatic": {"string_value": "Somatic"}, "Variant": {"string_value": "missense"}, "condons": {"string_value": "315"}, "cosmic_id": {"string_value": "12560"}, "coding_nucleotide": {"string_value": "944C>T"}, "transcript_id": {"string_value": "ENST00000318560"}}, "chromosome": "9"}, "source": "pmkb", "pmkb": {"tumor": "Chronic Myeloid Leukemia", "url": "https://pmkb.weill.cornell.edu/therapies/38", "tissues": ["Blood", "Bone Marrow"], "variant": {"amino_acid_change": "T315I", "name": "ABL1 T315I", "exons": "6", "url": "https://pmkb.weill.cornell.edu/genes/38/variants/101", "is_germline_somatic": "Somatic", "Variant": "missense", "condons": "315", "coordinates": "9:133748283-133748283", "cosmic_id": "12560", "coding_nucleotide": "944C>T", "transcript_id": "ENST00000318560", "Gene": "ABL1"}}, "gene": "ABL1", "association": {"drug_labels": "NA", "description": "ABL1 kinase domain mutations in Philadelphia chromosome positive acute lymphoblastic leukemia and chronic myelogenous leukemia are associated with resistance to some types of tryosine kinase inhibitor therapy. The various mutations span several hundred amino acids (M237 thru E507) and vary in their response to later generation tyrosine kinase inhibitors. ", "publication_url": "http://www.ncbi.nlm.nih.gov/pubmed/24382642", "evidence": [{"info": {"publications": [["http://www.ncbi.nlm.nih.gov/pubmed/24382642", "http://www.ncbi.nlm.nih.gov/pubmed/24131888"]]}, "evidenceType": {"sourceName": "pmkb"}, "description": "1"}], "evidence_label": "1", "phenotype": {"description": "Chronic Myeloid Leukemia"}}}
"""  # NOQA


def test_pmkb_pb():
    """ ensure we can de-serialize the message """
    harvested_evidence = json_format.Parse(
                                        PMKB_TEST_MESSAGE,
                                        evidence.Evidence(),
                                        ignore_unknown_fields=True)
    assert harvested_evidence.gene == "ABL1"
    assert harvested_evidence.source == "pmkb"
    assert harvested_evidence.feature.end == 133748283
    assert 'kinase domain mutations' in \
        harvested_evidence.association.description
    assert harvested_evidence.pmkb


def test_civic_pb():
    """ ensure we can de-serialize the message """
    harvested_evidence = json_format.Parse(
                                        CIVIC_TEST_MESSAGE,
                                        evidence.Evidence(),
                                        ignore_unknown_fields=True)
    assert harvested_evidence.gene == "CDKN2A"
    assert harvested_evidence.source == "civic"
    assert harvested_evidence.feature.end == 21974865
    assert 'expression' in harvested_evidence.association.description
    assert harvested_evidence.civic
    harvested_evidence.civic['evidence_items'][0]["clinical_significance"] == \
        "Better Outcome"


def test_jax_pb():
    """ ensure we can de-serialize the message """
    harvested_evidence = json_format.Parse(
                                        JAX_TEST_MESSAGE,
                                        evidence.Evidence(),
                                        ignore_unknown_fields=True)
    assert harvested_evidence.gene == "CDKN2A"
    assert harvested_evidence.source == "jax"
    assert harvested_evidence.feature.name == "CDKN2A loss"
    assert 'antagonized' in harvested_evidence.association.description
    assert harvested_evidence.jax
    harvested_evidence.jax['approval_status'] == 'Preclinical'


def test_oncokb_pb():
    """ ensure we can de-serialize the message """
    harvested_evidence = json_format.Parse(
                                        ONCOKB_TEST_MESSAGE,
                                        evidence.Evidence(),
                                        ignore_unknown_fields=True)
    assert harvested_evidence.gene == "CDKN2A"
    assert harvested_evidence.source == "oncokb"
    assert harvested_evidence.feature.name == "Oncogenic Mutations"
    assert 'NOT FDA-approved' in harvested_evidence.association.description
    assert harvested_evidence.oncokb
    assert harvested_evidence.oncokb['clinical']['cancerType']['mainType']['name'] == "Esophagogastric Cancer"  # NOQA


def test_molecular_match_pb():
    """ ensure we can de-serialize the message """
    harvested_evidence = json_format.Parse(
                                        MOLECULAR_MATCH_TEST_MESSAGE,
                                        evidence.Evidence(),
                                        ignore_unknown_fields=True)
    assert harvested_evidence.gene == "DDR2"
    assert harvested_evidence.source == "molecularmatch"
    assert harvested_evidence.feature.name == "DDR2 G505S"
    assert 'DDR2 G505S confers sensitivity' in \
        harvested_evidence.association.description
    assert harvested_evidence.molecularmatch['clinicalSignificance'] == 'sensitive'  # NOQA


def test_cgi_pb():
    """ ensure we can de-serialize the message """
    harvested_evidence = json_format.Parse(
                                        CGI_TEST_MESSAGE,
                                        evidence.Evidence(),
                                        ignore_unknown_fields=True)
    assert harvested_evidence.gene == "CDKN2A"
    assert harvested_evidence.source == "cgi"
    assert harvested_evidence.feature.name == "CDKN2A oncogenic mutation"
    assert 'CDKN2A CDK4/6 inhibitors Responsive' in \
        harvested_evidence.association.description
    assert harvested_evidence.cgi['Gene'] == 'CDKN2A'
