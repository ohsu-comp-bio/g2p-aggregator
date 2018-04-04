import molecularmatch

EVIDENCE = \
{
      "criteriaUnmet": [
        {
          "priority": 1,
          "term": "Medullary thyroid carcinoma",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "custom": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "Medullary thyroid carcinomaCONDITIONinclude"
        },
        {
          "priority": 1,
          "term": "RET V804L",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "RET V804LMUTATIONinclude",
          "custom": True,
          "facet": "MUTATION",
          "valid": True,
          "transcript": "NM_020975.4"
        }
      ],
      "civic": "N/A",
      "mboost": 0,
      "autoGenerateNarrative": True,
      "mutations": [
        {
          "pathology": [
            "Pathogenic"
          ],
          "name": "RET V804L",
          "transcriptRecognized": True,
          "wgsaData": {
            "location0": {
              "End": "43614996",
              "dbSNP": "rs79658334",
              "Start": "43614996",
              "Chr": "10",
              "FullAA": [
                "RET:NM_020975.4:exon14:c.2410G>C:p.V804L",
                "RET:NM_020630.4:exon14:c.2410G>C:p.V804L"
              ],
              "Ref": "G",
              "ClinVar_SIG": [
                "5"
              ],
              "GERP++_RS": "5.36",
              "SiPhy_29way_logOdds": "19.0766",
              "FATHMM": "ADB",
              "phyloP100way_vertebrate": "9.855",
              "NucleotideChange": "c.2410G>C",
              "Func": "exonic",
              "Transcript": "2IVS:A_756-A_804:NM_020630.4",
              "ClinVar_STATUS": [
                "0"
              ],
              "Chr_Start_Ref_Alt": "10_43614996_G_C",
              "ExonicFunc": "missense",
              "PopFreqMax": "0",
              "FATHMM_Pred": "D",
              "Gene": [
                "RET"
              ],
              "phyloP46way_placental": "2.518",
              "_key": "10_43614996_G_C",
              "ClinVar_DIS": [
                "MEN2 phenotype: Unclassified"
              ],
              "ClinVar_DBID": [
                "rs79658334"
              ],
              "Alt": "C"
            },
            "location1": {
              "End": "43614996",
              "ExAC_NFE": "2.858e-05",
              "ExAC_FIN": "0",
              "ExAC_SAS": "0",
              "Chr": "10",
              "ExAC_EAS": "0",
              "FullAA": [
                "RET:NM_020630.4:exon14:c.2410G>T:p.V804L",
                "RET:NM_020975.4:exon14:c.2410G>T:p.V804L"
              ],
              "Ref": "G",
              "ExAC_AMR": "0",
              "ClinVar_SIG": [
                "5",
                "5"
              ],
              "GERP++_RS": "5.36",
              "SiPhy_29way_logOdds": "19.0766",
              "FATHMM": "ADB",
              "phyloP100way_vertebrate": "9.855",
              "phyloP46way_placental": "2.518",
              "NucleotideChange": "c.2410G>T",
              "Func": "exonic",
              "Transcript": "2IVS:A_756-A_804:NM_020630.4",
              "ClinVar_STATUS": [
                "0",
                "0"
              ],
              "Chr_Start_Ref_Alt": "10_43614996_G_T",
              "ExonicFunc": "missense",
              "PopFreqMax": "2.858e-05",
              "FATHMM_Pred": "D",
              "Gene": [
                "RET"
              ],
              "dbSNP": "rs79658334",
              "Start": "43614996",
              "_key": "10_43614996_G_T",
              "ClinVar_DIS": [
                "Familial medullary thyroid carcinoma",
                "MEN2A and FMTC"
              ],
              "ClinVar_DBID": [
                "rs79658334"
              ],
              "ExAC_Freq": "1.569e-05",
              "ExAC_AFR": "0",
              "Alt": "T"
            }
          },
          "description": "",
          "mutation_type": [
            "Missense"
          ],
          "_src": 1,
          "GRCh38_location": [
            {
              "compositeKey": "ca4ecdb88afff1ab5a7617cb14805ce6",
              "stop": "43119548",
              "start": "43119548",
              "chr": "10",
              "alt": "C",
              "ref": "G",
              "strand": "+"
            },
            {
              "compositeKey": "5b61aeb94ee345fa8b1a516f556f8d97",
              "stop": "43119548",
              "start": "43119548",
              "chr": "10",
              "alt": "T",
              "ref": "G",
              "strand": "+"
            }
          ],
          "sources": [
            "ClinVar",
            "DoCM"
          ],
          "synonyms": [],
          "parents": [
            {
              "transcripts": [
                "NM_020630.4",
                "NM_020975.4"
              ],
              "type": "exon mutation",
              "name": "RET exon 14 mutation"
            },
            {
              "transcripts": [
                "NM_000061.2",
                "NM_000141.4",
                "NM_000142.4",
                "NM_000180.3",
                "NM_000208.2",
                "NM_000215.3",
                "NM_000222.2",
                "NM_000245.2",
                "NM_000459.4",
                "NM_000875.4",
                "NM_000906.3",
                "NM_001005862.2",
                "NM_001007792.1",
                "NM_001010938.1",
                "NM_001012331.1",
                "NM_001012338.2",
                "NM_001014794.2",
                "NM_001014796.1",
                "NM_001018064.2",
                "NM_001042599.1",
                "NM_001042729.1",
                "NM_001042771.2",
                "NM_001079.3",
                "NM_001079817.1",
                "NM_001080395.2",
                "NM_001080434.1",
                "NM_001080448.2",
                "NM_001093772.1",
                "NM_001099439.1",
                "NM_001111097.2",
                "NM_001127190.1",
                "NM_001127500.1",
                "NM_001135052.3",
                "NM_001136000.2",
                "NM_001136001.1",
                "NM_001143783.1",
                "NM_001143784.1",
                "NM_001143785.1",
                "NM_001144913.1",
                "NM_001144914.1",
                "NM_001144915.1",
                "NM_001144916.1",
                "NM_001144917.1",
                "NM_001144918.1",
                "NM_001144919.1",
                "NM_001163213.1",
                "NM_001168236.1",
                "NM_001168237.1",
                "NM_001168238.1",
                "NM_001168239.1",
                "NM_001172129.1",
                "NM_001172130.1",
                "NM_001172131.1",
                "NM_001172132.1",
                "NM_001174063.1",
                "NM_001174064.1",
                "NM_001174065.1",
                "NM_001174066.1",
                "NM_001174067.1",
                "NM_001174167.2",
                "NM_001193511.1",
                "NM_001199649.1",
                "NM_001201457.1",
                "NM_001202523.1",
                "NM_001204426.1",
                "NM_001242314.1",
                "NM_001244937.1",
                "NM_001251902.1",
                "NM_001253357.1",
                "NM_001256196.1",
                "NM_001270398.1",
                "NM_001278442.1",
                "NM_001278599.1",
                "NM_001281765.1",
                "NM_001281766.1",
                "NM_001281767.1",
                "NM_001287344.1",
                "NM_001288629.1",
                "NM_001288705.1",
                "NM_001289936.1",
                "NM_001289937.1",
                "NM_001290077.1",
                "NM_001290078.1",
                "NM_001291858.1",
                "NM_001291980.1",
                "NM_001297652.1",
                "NM_001297654.1",
                "NM_001304536.1",
                "NM_001304537.1",
                "NM_001522.2",
                "NM_001654.4",
                "NM_001699.5",
                "NM_001715.2",
                "NM_001721.6",
                "NM_001982.3",
                "NM_002005.3",
                "NM_002011.4",
                "NM_002019.4",
                "NM_002020.4",
                "NM_002031.2",
                "NM_002037.5",
                "NM_002110.3",
                "NM_002227.2",
                "NM_002253.2",
                "NM_002314.3",
                "NM_002344.5",
                "NM_002350.3",
                "NM_002378.3",
                "NM_002419.3",
                "NM_002446.3",
                "NM_002447.2",
                "NM_002529.3",
                "NM_002609.3",
                "NM_002821.4",
                "NM_002880.3",
                "NM_002944.2",
                "NM_003188.3",
                "NM_003215.2",
                "NM_003328.2",
                "NM_003331.4",
                "NM_003804.3",
                "NM_003985.4",
                "NM_003995.3",
                "NM_004103.4",
                "NM_004119.2",
                "NM_004304.4",
                "NM_004333.4",
                "NM_004431.3",
                "NM_004439.6",
                "NM_004440.3",
                "NM_004441.4",
                "NM_004442.6",
                "NM_004443.3",
                "NM_004444.4",
                "NM_004445.5",
                "NM_004448.3",
                "NM_004560.3",
                "NM_004920.2",
                "NM_004963.3",
                "NM_004972.3",
                "NM_005012.3",
                "NM_005157.5",
                "NM_005158.4",
                "NM_005228.3",
                "NM_005232.4",
                "NM_005233.5",
                "NM_005235.2",
                "NM_005246.2",
                "NM_005417.4",
                "NM_005424.4",
                "NM_005433.3",
                "NM_005546.3",
                "NM_005569.3",
                "NM_005607.4",
                "NM_005781.4",
                "NM_005975.3",
                "NM_006180.4",
                "NM_006206.4",
                "NM_006293.3",
                "NM_006301.3",
                "NM_006343.2",
                "NM_007170.2",
                "NM_007313.2",
                "NM_007314.3",
                "NM_014215.2",
                "NM_014916.3",
                "NM_015978.2",
                "NM_016653.2",
                "NM_016733.2",
                "NM_017449.3",
                "NM_018423.2",
                "NM_020526.3",
                "NM_020630.4",
                "NM_020975.4",
                "NM_021913.4",
                "NM_022963.3",
                "NM_022965.3",
                "NM_022970.3",
                "NM_023029.2",
                "NM_023106.2",
                "NM_023110.2",
                "NM_031272.4",
                "NM_032435.2",
                "NM_080823.3",
                "NM_133646.2",
                "NM_139354.2",
                "NM_139355.2",
                "NM_145331.2",
                "NM_145332.2",
                "NM_145333.2",
                "NM_152649.2",
                "NM_152880.3",
                "NM_152881.3",
                "NM_152882.3",
                "NM_153831.3",
                "NM_173175.2",
                "NM_173598.4",
                "NM_178510.1",
                "NM_182472.3",
                "NM_182925.4",
                "NM_198393.3",
                "NM_206961.3",
                "NM_207519.1"
              ],
              "type": "gatekeeper",
              "name": "Pkinase_Tyr 109 gatekeeper"
            },
            {
              "transcripts": [
                "NM_020630.4",
                "NM_020975.4"
              ],
              "type": "domain",
              "name": "RET Pkinase_Tyr domain"
            }
          ],
          "GRCh37_location": [
            {
              "compositeKey": "fb61ef82cd88fa33afd5b0d455358dc0",
              "transcript_consequences": [
                {
                  "amino_acid_change": "V804L",
                  "exonNumber": "14",
                  "txSites": [
                    "NM_020630.4:804"
                  ],
                  "transcript": "NM_020630.4",
                  "cdna": "c.2410G>C"
                },
                {
                  "amino_acid_change": "V804L",
                  "exonNumber": "14",
                  "txSites": [
                    "NM_020975.4:804"
                  ],
                  "transcript": "NM_020975.4",
                  "cdna": "c.2410G>C"
                }
              ],
              "stop": 43614996,
              "start": 43614996,
              "chr": "10",
              "alt": "C",
              "validated": "tute",
              "ref": "G",
              "strand": "+",
              "compositeKeyReverse": "10_43614996_C_G"
            },
            {
              "compositeKey": "d236c3733b23ba5b12dabf63bdce19a7",
              "transcript_consequences": [
                {
                  "amino_acid_change": "V804L",
                  "exonNumber": "14",
                  "txSites": [
                    "NM_020630.4:804"
                  ],
                  "transcript": "NM_020630.4",
                  "cdna": "c.2410G>T"
                },
                {
                  "amino_acid_change": "V804L",
                  "exonNumber": "14",
                  "txSites": [
                    "NM_020975.4:804"
                  ],
                  "transcript": "NM_020975.4",
                  "cdna": "c.2410G>T"
                }
              ],
              "stop": 43614996,
              "start": 43614996,
              "chr": "10",
              "alt": "T",
              "validated": "tute",
              "ref": "G",
              "strand": "+",
              "compositeKeyReverse": "10_43614996_C_A"
            },
            {
              "compositeKey": "fb61ef82cd88fa33afd5b0d455358dc0",
              "transcript_consequences": [
                {
                  "amino_acid_change": "V804L",
                  "exonNumber": "14",
                  "txSites": [
                    "NM_020630.4:804"
                  ],
                  "transcript": "NM_020630.4",
                  "cdna": "c.2410G>C"
                },
                {
                  "amino_acid_change": "V804L",
                  "exonNumber": "14",
                  "txSites": [
                    "NM_020975.4:804"
                  ],
                  "transcript": "NM_020975.4",
                  "cdna": "c.2410G>C"
                }
              ],
              "stop": 43614996,
              "start": 43614996,
              "chr": "10",
              "alt": "C",
              "validated": "tute",
              "ref": "G",
              "strand": "+",
              "compositeKeyReverse": "10_43614996_C_G"
            }
          ],
          "uniprotTranscript": "NM_020975.4",
          "geneSymbol": "RET",
          "transcripts": [
            {
              "CCDS": [
                "CCDS53525.1"
              ],
              "RefSeq": "NM_020630.4",
              "display": "NM_020630.4 / CCDS53525.1 / ENST00000340058.5",
              "Ensembl": [
                "ENST00000340058.5"
              ]
            },
            {
              "CCDS": [
                "CCDS7200.1"
              ],
              "RefSeq": "NM_020975.4",
              "display": "NM_020975.4 / CCDS7200.1 / ENST00000355710.3",
              "Ensembl": [
                "ENST00000355710.3"
              ]
            }
          ],
          "wgsaMap": [
            {
              "AA": "p.V804L",
              "name": "RET V804L",
              "GRCh37_Chr_Start_Ref_Alt": "10_43614996_G_T",
              "Synonyms": [
                "CCDS7200.1 p.V804L",
                "P07949 V804L",
                "NP_066124.1 p.V804L",
                "CCDS7200.1 c.2410G>T",
                "NP_066124.1 V804L",
                "NP_066124.1 c.2410G>T",
                "NM_020975.4 c.2410G>T",
                "ENSP00000347942.3 V804L",
                "RET p.V804L",
                "ENST00000355710.3 V804L",
                "CCDS7200.1 V804L",
                "ENSP00000347942.3 c.2410G>T",
                "P07949 c.2410G>T",
                "P07949 p.V804L",
                "ENST00000355710.3 c.2410G>T",
                "ENST00000355710.3 p.V804L",
                "NM_020975.4 V804L",
                "NM_020975.4 p.V804L",
                "ENSP00000347942.3 p.V804L",
                "rs79658334"
              ],
              "ProtCoords": [
                "NM_020975.4:804"
              ],
              "NucleotideChange": "c.2410G>T",
              "Exon": "exon14",
              "Gene": "RET",
              "Transcript": "NM_020975.4"
            },
            {
              "AA": "p.V804L",
              "name": "RET V804L",
              "GRCh37_Chr_Start_Ref_Alt": "10_43614996_G_C",
              "Synonyms": [
                "NM_020975.4 c.2410G>C",
                "CCDS7200.1 p.V804L",
                "P07949 V804L",
                "NP_066124.1 p.V804L",
                "NP_066124.1 V804L",
                "ENSP00000347942.3 V804L",
                "RET p.V804L",
                "ENSP00000347942.3 c.2410G>C",
                "P07949 c.2410G>C",
                "ENST00000355710.3 V804L",
                "ENST00000355710.3 c.2410G>C",
                "CCDS7200.1 V804L",
                "P07949 p.V804L",
                "ENST00000355710.3 p.V804L",
                "NM_020975.4 V804L",
                "NM_020975.4 p.V804L",
                "ENSP00000347942.3 p.V804L",
                "CCDS7200.1 c.2410G>C",
                "NP_066124.1 c.2410G>C",
                "rs79658334"
              ],
              "ProtCoords": [
                "NM_020975.4:804"
              ],
              "NucleotideChange": "c.2410G>C",
              "Exon": "exon14",
              "Gene": "RET",
              "Transcript": "NM_020975.4"
            }
          ],
          "transcript": "NM_020975.4",
          "id": "ret_v804l",
          "cdna": [
            "c.2410G>C",
            "c.2410G>T"
          ],
          "longestTranscript": "NM_020975.4"
        }
      ],
      "sources": [
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "15184865",
          "subType": "cell_line",
          "valid": True,
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/15184865",
          "year": "",
          "type": "preclinical",
          "id": "1"
        }
      ],
      "clinicalSignificance": "resistant",
      "id": "lbcp_3061",
      "includeCondition0": [
        "Malignant neoplasm of endocrine gland",
        "Neoplasm of endocrine system",
        "Malignant tumour of neck",
        "Malignant neoplastic disease",
        "Primary malignant neoplasm of endocrine gland",
        "Primary malignant neoplasm of thyroid gland",
        "Neuroendocrine tumour",
        "Neoplasm of head and neck",
        "Primary malignant neoplasm of neck",
        "Neoplasm of endocrine gland",
        "Neoplasm of thyroid gland",
        "Neoplasia",
        "Solid tumor"
      ],
      "includeCondition1": [
        "Medullary thyroid carcinoma"
      ],
      "uniqueKey": "3818a952ae43704230254c5915a3980e",
      "prevalence": [
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER MAX"
        },
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER AVG"
        }
      ],
      "regulatoryBodyApproved": False,
      "version": 1,
      "includeMutation1": [
        "RET V804L"
      ],
      "includeMutation0": [
        "RET exon 14 mutation",
        "RET Pkinase_Tyr domain",
        "Pkinase_Tyr 109 gatekeeper"
      ],
      "regulatoryBody": "FDA",
      "direction": "supports",
      "ampcap": "2D",
      "ast": {
        "operator": "&&",
        "right": {
          "raw": "\"RET V804L\"",
          "type": "Literal",
          "value": "RET V804L"
        },
        "type": "LogicalExpression",
        "left": {
          "raw": "\"Medullary thyroid carcinoma\"",
          "type": "Literal",
          "value": "Medullary thyroid carcinoma"
        }
      },
      "tier": "3",
      "tierExplanation": [
        {
          "tier": "1",
          "step": 1,
          "message": "FDA Approved",
          "success": False
        },
        {
          "tier": "1",
          "step": 2,
          "message": "No guideline established",
          "success": False
        },
        {
          "tier": "2",
          "step": 3,
          "message": "Source (trial, case_study, expert) found",
          "success": False
        },
        {
          "tier": "3",
          "step": 4,
          "message": "Source (preclinical, institutional_study) found",
          "success": True
        },
        {
          "tier": "4",
          "step": 5,
          "message": "Source (pathway_inferred) found",
          "success": False
        },
        {
          "tier": "5",
          "step": 6,
          "message": "Source (sequencing) found",
          "success": False
        },
        {
          "tier": "5",
          "step": 7,
          "message": "Unknown Biomarker Class",
          "success": False
        }
      ],
      "mvld": "3",
      "tags": [
        {
          "priority": 1,
          "term": "Medullary thyroid carcinoma",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "custom": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "Medullary thyroid carcinomaCONDITIONinclude"
        },
        {
          "priority": 1,
          "term": "RET V804L",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "RET V804LMUTATIONinclude",
          "custom": True,
          "facet": "MUTATION",
          "valid": True,
          "transcript": "NM_020975.4"
        },
        {
          "priority": 0,
          "term": "RET",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "GENE",
          "generatedByTerm": "RET V804L"
        },
        {
          "priority": 0,
          "term": "RET exon 14 mutation",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "MUTATION",
          "generatedByTerm": "RET V804L"
        },
        {
          "priority": 0,
          "term": "RET Pkinase_Tyr domain",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "MUTATION",
          "generatedByTerm": "RET V804L"
        },
        {
          "priority": 0,
          "term": "Pkinase_Tyr 109 gatekeeper",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "MUTATION",
          "generatedByTerm": "RET V804L"
        },
        {
          "priority": 0,
          "term": "Malignant neoplasm of endocrine gland",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Neoplasm of endocrine system",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Malignant tumour of neck",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Malignant neoplastic disease",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Primary malignant neoplasm of endocrine gland",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Primary malignant neoplasm of thyroid gland",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Neuroendocrine tumour",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Neoplasm of head and neck",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Primary malignant neoplasm of neck",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Neoplasm of endocrine gland",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Neoplasm of thyroid gland",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Neoplasia",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Solid tumor",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Medullary thyroid carcinoma"
        },
        {
          "priority": 0,
          "term": "Thyroid",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "SITE",
          "generatedByTerm": "Medullary thyroid carcinoma"
        }
      ],
      "customer": "LabCorp",
      "biomarkerClass": "predictive",
      "classifications": [
        {
          "cbioportal_prevalence": [],
          "classification": "unknown",
          "copyNumberType": None,
          "sources": [
            "ClinVar",
            "DoCM"
          ],
          "Chr": [
            "10"
          ],
          "geneSymbol": "RET",
          "pathology": [
            "Pathogenic"
          ],
          "Ref": [
            "G"
          ],
          "description": "",
          "End": [
            "43614996"
          ],
          "priority": 2,
          "NucleotideChange": [
            "c.2410G>T",
            "c.2410G>C"
          ],
          "expandGeneSearch": False,
          "Exon": [
            "14"
          ],
          "drugsApprovedOffLabelCount": 0,
          "parents": [
            {
              "transcripts": [
                "NM_020630.4",
                "NM_020975.4"
              ],
              "type": "exon mutation",
              "name": "RET exon 14 mutation"
            },
            {
              "transcripts": [
                "NM_000061.2",
                "NM_000141.4",
                "NM_000142.4",
                "NM_000180.3",
                "NM_000208.2",
                "NM_000215.3",
                "NM_000222.2",
                "NM_000245.2",
                "NM_000459.4",
                "NM_000875.4",
                "NM_000906.3",
                "NM_001005862.2",
                "NM_001007792.1",
                "NM_001010938.1",
                "NM_001012331.1",
                "NM_001012338.2",
                "NM_001014794.2",
                "NM_001014796.1",
                "NM_001018064.2",
                "NM_001042599.1",
                "NM_001042729.1",
                "NM_001042771.2",
                "NM_001079.3",
                "NM_001079817.1",
                "NM_001080395.2",
                "NM_001080434.1",
                "NM_001080448.2",
                "NM_001093772.1",
                "NM_001099439.1",
                "NM_001111097.2",
                "NM_001127190.1",
                "NM_001127500.1",
                "NM_001135052.3",
                "NM_001136000.2",
                "NM_001136001.1",
                "NM_001143783.1",
                "NM_001143784.1",
                "NM_001143785.1",
                "NM_001144913.1",
                "NM_001144914.1",
                "NM_001144915.1",
                "NM_001144916.1",
                "NM_001144917.1",
                "NM_001144918.1",
                "NM_001144919.1",
                "NM_001163213.1",
                "NM_001168236.1",
                "NM_001168237.1",
                "NM_001168238.1",
                "NM_001168239.1",
                "NM_001172129.1",
                "NM_001172130.1",
                "NM_001172131.1",
                "NM_001172132.1",
                "NM_001174063.1",
                "NM_001174064.1",
                "NM_001174065.1",
                "NM_001174066.1",
                "NM_001174067.1",
                "NM_001174167.2",
                "NM_001193511.1",
                "NM_001199649.1",
                "NM_001201457.1",
                "NM_001202523.1",
                "NM_001204426.1",
                "NM_001242314.1",
                "NM_001244937.1",
                "NM_001251902.1",
                "NM_001253357.1",
                "NM_001256196.1",
                "NM_001270398.1",
                "NM_001278442.1",
                "NM_001278599.1",
                "NM_001281765.1",
                "NM_001281766.1",
                "NM_001281767.1",
                "NM_001287344.1",
                "NM_001288629.1",
                "NM_001288705.1",
                "NM_001289936.1",
                "NM_001289937.1",
                "NM_001290077.1",
                "NM_001290078.1",
                "NM_001291858.1",
                "NM_001291980.1",
                "NM_001297652.1",
                "NM_001297654.1",
                "NM_001304536.1",
                "NM_001304537.1",
                "NM_001522.2",
                "NM_001654.4",
                "NM_001699.5",
                "NM_001715.2",
                "NM_001721.6",
                "NM_001982.3",
                "NM_002005.3",
                "NM_002011.4",
                "NM_002019.4",
                "NM_002020.4",
                "NM_002031.2",
                "NM_002037.5",
                "NM_002110.3",
                "NM_002227.2",
                "NM_002253.2",
                "NM_002314.3",
                "NM_002344.5",
                "NM_002350.3",
                "NM_002378.3",
                "NM_002419.3",
                "NM_002446.3",
                "NM_002447.2",
                "NM_002529.3",
                "NM_002609.3",
                "NM_002821.4",
                "NM_002880.3",
                "NM_002944.2",
                "NM_003188.3",
                "NM_003215.2",
                "NM_003328.2",
                "NM_003331.4",
                "NM_003804.3",
                "NM_003985.4",
                "NM_003995.3",
                "NM_004103.4",
                "NM_004119.2",
                "NM_004304.4",
                "NM_004333.4",
                "NM_004431.3",
                "NM_004439.6",
                "NM_004440.3",
                "NM_004441.4",
                "NM_004442.6",
                "NM_004443.3",
                "NM_004444.4",
                "NM_004445.5",
                "NM_004448.3",
                "NM_004560.3",
                "NM_004920.2",
                "NM_004963.3",
                "NM_004972.3",
                "NM_005012.3",
                "NM_005157.5",
                "NM_005158.4",
                "NM_005228.3",
                "NM_005232.4",
                "NM_005233.5",
                "NM_005235.2",
                "NM_005246.2",
                "NM_005417.4",
                "NM_005424.4",
                "NM_005433.3",
                "NM_005546.3",
                "NM_005569.3",
                "NM_005607.4",
                "NM_005781.4",
                "NM_005975.3",
                "NM_006180.4",
                "NM_006206.4",
                "NM_006293.3",
                "NM_006301.3",
                "NM_006343.2",
                "NM_007170.2",
                "NM_007313.2",
                "NM_007314.3",
                "NM_014215.2",
                "NM_014916.3",
                "NM_015978.2",
                "NM_016653.2",
                "NM_016733.2",
                "NM_017449.3",
                "NM_018423.2",
                "NM_020526.3",
                "NM_020630.4",
                "NM_020975.4",
                "NM_021913.4",
                "NM_022963.3",
                "NM_022965.3",
                "NM_022970.3",
                "NM_023029.2",
                "NM_023106.2",
                "NM_023110.2",
                "NM_031272.4",
                "NM_032435.2",
                "NM_080823.3",
                "NM_133646.2",
                "NM_139354.2",
                "NM_139355.2",
                "NM_145331.2",
                "NM_145332.2",
                "NM_145333.2",
                "NM_152649.2",
                "NM_152880.3",
                "NM_152881.3",
                "NM_152882.3",
                "NM_153831.3",
                "NM_173175.2",
                "NM_173598.4",
                "NM_178510.1",
                "NM_182472.3",
                "NM_182925.4",
                "NM_198393.3",
                "NM_206961.3",
                "NM_207519.1"
              ],
              "type": "gatekeeper",
              "name": "Pkinase_Tyr 109 gatekeeper"
            },
            {
              "transcripts": [
                "NM_020630.4",
                "NM_020975.4"
              ],
              "type": "domain",
              "name": "RET Pkinase_Tyr domain"
            }
          ],
          "ExonicFunc": [
            "missense"
          ],
          "drugsExperimentalCount": 0,
          "PopFreqMax": [
            0.00002858,
            0
          ],
          "publicationCount": 11,
          "transcript": None,
          "Alt": [
            "T",
            "C"
          ],
          "name": "RET V804L",
          "rootTerm": "RET V804L",
          "Start": [
            "43614996"
          ],
          "drugsApprovedOnLabelCount": 0,
          "trialCount": 0,
          "alias": "RET V804L",
          "COSMIC_ID": [],
          "dbSNP": [
            "rs79658334"
          ],
          "transcripts": [
            {
              "CCDS": [
                "CCDS53525.1"
              ],
              "RefSeq": "NM_020630.4",
              "display": "NM_020630.4 / CCDS53525.1 / ENST00000340058.5",
              "Ensembl": [
                "ENST00000340058.5"
              ]
            },
            {
              "CCDS": [
                "CCDS7200.1"
              ],
              "RefSeq": "NM_020975.4",
              "display": "NM_020975.4 / CCDS7200.1 / ENST00000355710.3",
              "Ensembl": [
                "ENST00000355710.3"
              ]
            }
          ]
        }
      ],
      "therapeuticContext": [
        {
          "facet": "PHRASE",
          "suppress": False,
          "valid": False,
          "name": "vandetinib"
        }
      ],
      "expression": "\"Medullary thyroid carcinoma\" && \"RET V804L\"",
      "sixtier": "5",
      "narrative": "RET V804L confers resistance to vandetinib in patients with Medullary thyroid carcinoma",
      "external_id": [
        "RET_40"
      ],
      "includeGene0": [
        "RET"
      ]
    }


EVIDENCE2 = \
{
      "criteriaUnmet": [
        {
          "priority": 1,
          "compositeKey": "Neoplasm of colorectumCONDITIONinclude",
          "isNew": "",
          "suppress": False,
          "generatedBy": "",
          "filterType": "include",
          "term": "Neoplasm of colorectum",
          "primary": True,
          "facet": "CONDITION",
          "valid": True,
          "manualSuppress": 0,
          "generatedByTerm": ""
        },
        {
          "priority": 1,
          "compositeKey": "UGT1A1*28MUTATIONinclude",
          "isNew": "",
          "suppress": False,
          "generatedBy": "",
          "filterType": "include",
          "term": "UGT1A1 UGT1A1*28",
          "primary": "",
          "facet": "MUTATION",
          "valid": True,
          "manualSuppress": 0,
          "generatedByTerm": ""
        },
        {
          "priority": 1,
          "compositeKey": "UGT1A1*37MUTATIONinclude",
          "isNew": True,
          "suppress": False,
          "generatedBy": "",
          "filterType": "include",
          "term": "UGT1A1*37",
          "primary": False,
          "facet": "MUTATION",
          "valid": True,
          "manualSuppress": 0,
          "generatedByTerm": ""
        }
      ],
      "prevalence": [
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER MAX"
        },
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER AVG"
        }
      ],
      "mboost": 0,
      "autoGenerateNarrative": True,
      "mutations": [
        {
          "name": "UGT1A1*37",
          "classification": "unknown",
          "mutation_type": [
            "Regulatory Region Variant"
          ],
          "_src": 1,
          "GRCh38_location": [],
          "sources": [],
          "synonyms": [],
          "parents": [],
          "GRCh37_location": [
            {
              "compositeKey": "699a7b0ea57bd30921a85dedcd4bf0fa",
              "stop": "234668880",
              "custom": True,
              "start": "234668879",
              "chr": "2",
              "alt": "ATAT",
              "validated": "MolecularMatch",
              "ref": "-",
              "strand": "+"
            }
          ],
          "geneSymbol": "UGT1A1",
          "pathology": [],
          "id": "758bc98783aa08f395ac444bdd9491d9",
          "cdna": [],
          "description": ""
        },
        {
          "pathology": [],
          "name": "UGT1A1 UGT1A1*28",
          "classification": "actionable",
          "description": "The FDA approved package insert for Belinostat recommends dose adjustment for UGT1A1*28 allele homozygotes. (CIViC)",
          "mutation_type": [
            "Snp",
            "Microsatellite"
          ],
          "_src": 1,
          "GRCh38_location": [],
          "sources": [
            "CIViC"
          ],
          "synonyms": [],
          "parents": [],
          "GRCh37_location": [
            {
              "compositeKey": "57aae3bc23223961e0714dc566220924",
              "stop": "234668880",
              "custom": True,
              "start": "234668879",
              "chr": "2",
              "alt": "AT",
              "validated": "MolecularMatch",
              "ref": "-",
              "strand": "+"
            }
          ],
          "uniprotTranscript": "NM_000463.2",
          "geneSymbol": "UGT1A1",
          "transcripts": [
            {
              "CCDS": [
                "CCDS2510.1"
              ],
              "RefSeq": "NM_000463.2",
              "display": "NM_000463.2 / CCDS2510.1 / ENST00000305208.5",
              "Ensembl": [
                "ENST00000305208.5"
              ]
            }
          ],
          "transcript": "NM_000463.2",
          "id": "ugt1a1_ugt1a1*28",
          "cdna": [],
          "longestTranscript": "NM_000463.2"
        }
      ],
      "civic": "N/A",
      "sources": [
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "16809730",
          "year": "",
          "institution": "",
          "subType": "researcher",
          "link": "",
          "type": "expert",
          "trialPhase": "",
          "trialId": "",
          "id": "1493161996520"
        },
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "20335017",
          "year": "",
          "institution": "",
          "subType": "retrospective",
          "link": "",
          "type": "institutional_study",
          "trialPhase": "",
          "trialId": "",
          "id": "1493161837166"
        },
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "11990381",
          "year": "",
          "institution": "",
          "subType": "prospective",
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/11990381",
          "type": "trial",
          "trialPhase": "",
          "trialId": "",
          "id": "1"
        },
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "19364970",
          "year": "",
          "institution": "",
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/19364970",
          "type": "regulatory",
          "trialPhase": "",
          "trialId": "",
          "id": "2"
        },
        {
          "name": "",
          "suppress": False,
          "pubId": "",
          "year": "",
          "institution": "",
          "link": "https://www.ncbi.nlm.nih.gov/books/nbk294473/",
          "type": "regulatory",
          "trialPhase": "",
          "trialId": "",
          "id": "3"
        },
        {
          "name": "",
          "suppress": False,
          "pubId": "",
          "year": "",
          "institution": "",
          "link": "https://www.fda.gov/ohrms/dockets/ac/04/briefing/2004-4079b1_07_pfizer-ugt1a1.pdf",
          "type": "regulatory",
          "trialPhase": "",
          "trialId": "",
          "id": "4"
        }
      ],
      "clinicalSignificance": "unfavorable",
      "id": "crc-r-118",
      "includeCondition0": [
        "Neoplasm of intestinal tract",
        "Neoplasm of large intestine",
        "Tumour of gastrointestinal tract",
        "Neoplasm of rectum",
        "Neoplasia",
        "Neoplasm of intra-abdominal organs",
        "Solid tumor",
        "Malignant neoplastic disease",
        "Neoplasm of digestive tract",
        "Neoplasm of digestive system",
        "Neoplasm of digestive organ",
        "Neoplasm of colon"
      ],
      "includeCondition1": [
        "Neoplasm of colorectum"
      ],
      "uniqueKey": "d55dc02b8af0a412af209d0260d64dac",
      "tags": [
        {
          "priority": 1,
          "compositeKey": "UGT1A1*37MUTATIONinclude",
          "isNew": True,
          "suppress": False,
          "generatedBy": "",
          "filterType": "include",
          "term": "UGT1A1*37",
          "primary": False,
          "facet": "MUTATION",
          "valid": True,
          "manualSuppress": 0,
          "generatedByTerm": ""
        },
        {
          "priority": 1,
          "compositeKey": "Neoplasm of colorectumCONDITIONinclude",
          "isNew": "",
          "suppress": False,
          "generatedBy": "",
          "filterType": "include",
          "term": "Neoplasm of colorectum",
          "primary": True,
          "facet": "CONDITION",
          "valid": True,
          "manualSuppress": 0,
          "generatedByTerm": ""
        },
        {
          "priority": 1,
          "compositeKey": "UGT1A1*28MUTATIONinclude",
          "isNew": "",
          "suppress": False,
          "generatedBy": "",
          "filterType": "include",
          "term": "UGT1A1 UGT1A1*28",
          "primary": "",
          "facet": "MUTATION",
          "valid": True,
          "manualSuppress": 0,
          "generatedByTerm": ""
        },
        {
          "priority": 0,
          "term": "UGT1A1",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "GENE",
          "generatedByTerm": "UGT1A1*37"
        },
        {
          "priority": 0,
          "term": "Neoplasm of intestinal tract",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of large intestine",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Tumour of gastrointestinal tract",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of rectum",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasia",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of intra-abdominal organs",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Solid tumor",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Malignant neoplastic disease",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of digestive tract",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of digestive system",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of digestive organ",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of colon",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Entire colon",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "SITE",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Rectum",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "SITE",
          "generatedByTerm": "Neoplasm of colorectum"
        }
      ],
      "mvld": "1",
      "regulatoryBodyApproved": True,
      "version": 1,
      "includeMutation1": [
        "UGT1A1*37",
        "UGT1A1 UGT1A1*28"
      ],
      "guidelineBody": "",
      "regulatoryBody": "FDA",
      "direction": "supports",
      "ampcap": "1A",
      "ast": {
        "operator": "&&",
        "right": {
          "operator": "||",
          "right": {
            "raw": "\"UGT1A1*37\"",
            "type": "Literal",
            "value": "UGT1A1*37"
          },
          "type": "LogicalExpression",
          "left": {
            "raw": "\"UGT1A1 UGT1A1*28\"",
            "type": "Literal",
            "value": "UGT1A1 UGT1A1*28"
          }
        },
        "type": "LogicalExpression",
        "left": {
          "raw": "\"Neoplasm of colorectum\"",
          "type": "Literal",
          "value": "Neoplasm of colorectum"
        }
      },
      "guidelineVersion": "",
      "tier": "1",
      "tierExplanation": [
        {
          "tier": "1",
          "step": 1,
          "message": "FDA Approved",
          "success": True
        }
      ],
      "institution": [],
      "customer": "MolecularMatch",
      "biomarkerClass": "predictive",
      "classifications": [
        {
          "name": "UGT1A1*37",
          "classification": "unknown"
        },
        {
          "name": "UGT1A1 UGT1A1*28",
          "classification": "actionable"
        }
      ],
      "therapeuticContext": [
        {
          "facet": "DRUG",
          "suppress": False,
          "valid": True,
          "name": "Irinotecan hydrochloride"
        }
      ],
      "includeDrug1": [
        "Irinotecan hydrochloride"
      ],
      "sixtier": "1",
      "narrative": "UGT1A1*37 and UGT1A1 UGT1A1*28 confers an unfavorable response to Irinotecan hydrochloride in patients with Neoplasm of colorectum",
      "expression": "\"Neoplasm of colorectum\" && (\"UGT1A1 UGT1A1*28\" || \"UGT1A1*37\")",
      "includeGene0": [
        "UGT1A1"
      ]
    }

EVIDENCE3 =  {
      "criteriaUnmet": [
        {
          "priority": 1,
          "term": "Neoplasm of lung",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "custom": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "Neoplasm of lungCONDITIONinclude"
        },
        {
          "priority": 1,
          "term": "MAP2K1 I103N",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "MAP2K1 I103NMUTATIONinclude",
          "custom": True,
          "facet": "MUTATION",
          "valid": True
        }
      ],
      "civic": "N/A",
      "mboost": 0,
      "autoGenerateNarrative": True,
      "mutations": [
        {
          "pathology": [],
          "classification": "informative",
          "name": "MAP2K1 I103N",
          "wgsaData": {
            "location0": {
              "AA": "p.I103N",
              "End": "66729100",
              "Start": "66729100",
              "SiPhy_29way_logOdds": "14.802",
              "FullAA": [
                "MAP2K1:NM_002755.3:exon3:c.308T>A:p.I103N"
              ],
              "Ref": "T",
              "GERP++_RS": "5.04",
              "FATHMM": "AB",
              "phyloP100way_vertebrate": "7.888",
              "NucleotideChange": "c.308T>A",
              "Func": "exonic",
              "Transcript": "NM_002755.3",
              "Chr_Start_Ref_Alt": "15_66729100_T_A",
              "ExonicFunc": "missense",
              "PopFreqMax": "0",
              "FATHMM_Pred": "D",
              "Gene": [
                "MAP2K1"
              ],
              "phyloP46way_placental": "1.888",
              "_key": "15_66729100_T_A",
              "Chr": "15",
              "COSMIC_ID": "COSM3728157",
              "Alt": "A"
            }
          },
          "description": "",
          "mutation_type": [
            "Missense"
          ],
          "_src": 1,
          "GRCh38_location": [],
          "sources": [
            "COSMIC",
            "DoCM"
          ],
          "synonyms": [],
          "parents": [
            {
              "transcripts": [
                "NM_002755.3"
              ],
              "type": "exon mutation",
              "name": "MAP2K1 exon 3 mutation"
            },
            {
              "transcripts": [
                "NM_002755.3"
              ],
              "type": "domain",
              "name": "MAP2K1 Pkinase domain"
            },
            {
              "transcripts": [],
              "type": None,
              "name": "MEKi resistance mutations"
            }
          ],
          "GRCh37_location": [
            {
              "compositeKey": "b5b0c04dc7aecb6cbc2805cd6004f3bb",
              "transcript_consequences": [
                {
                  "amino_acid_change": "I103N",
                  "exonNumber": "3",
                  "txSites": [
                    "NM_002755.3:103"
                  ],
                  "transcript": "NM_002755.3",
                  "cdna": "c.308T>A"
                }
              ],
              "stop": 66729100,
              "start": 66729100,
              "chr": "15",
              "alt": "A",
              "validated": "tute",
              "ref": "T",
              "strand": "+",
              "compositeKeyReverse": "15_66729100_A_T"
            },
            {
              "compositeKey": "b5b0c04dc7aecb6cbc2805cd6004f3bb",
              "transcript_consequences": [
                {
                  "amino_acid_change": "I103N",
                  "exonNumber": "3",
                  "txSites": [
                    "NM_002755.3:103"
                  ],
                  "transcript": "NM_002755.3",
                  "cdna": "c.308T>A"
                }
              ],
              "stop": 66729100,
              "start": 66729100,
              "chr": "15",
              "alt": "A",
              "validated": "tute",
              "ref": "T",
              "strand": "+",
              "compositeKeyReverse": "15_66729100_A_T"
            }
          ],
          "uniprotTranscript": "NM_002755.3",
          "geneSymbol": "MAP2K1",
          "transcripts": [
            {
              "CCDS": [
                "CCDS10216.1"
              ],
              "RefSeq": "NM_002755.3",
              "display": "NM_002755.3 / CCDS10216.1 / ENST00000307102.5",
              "Ensembl": [
                "ENST00000307102.5"
              ]
            }
          ],
          "wgsaMap": [
            {
              "AA": "p.I103N",
              "name": "MAP2K1 I103N",
              "GRCh37_Chr_Start_Ref_Alt": "15_66729100_T_A",
              "Synonyms": [
                "ENST00000307102.5 c.308T>A",
                "NM_002755.3 I103N",
                "NM_002755.3 c.308T>A",
                "ENSP00000302486.4 c.308T>A",
                "ENSP00000302486.4 p.I103N",
                "NP_002746.1 p.I103N",
                "CCDS10216.1 c.308T>A",
                "MAP2K1 p.I103N",
                "NP_002746.1 c.308T>A",
                "NM_002755.3 p.I103N",
                "ENSP00000302486.4 I103N",
                "NP_002746.1 I103N",
                "ENST00000307102.5 I103N",
                "ENST00000307102.5 p.I103N",
                "CCDS10216.1 p.I103N",
                "Q02750 I103N",
                "CCDS10216.1 I103N",
                "Q02750 c.308T>A",
                "Q02750 p.I103N"
              ],
              "ProtCoords": [
                "NM_002755.3:103"
              ],
              "NucleotideChange": "c.308T>A",
              "Exon": "exon3",
              "Gene": "MAP2K1",
              "Transcript": "NM_002755.3"
            }
          ],
          "transcript": "NM_002755.3",
          "id": "map2k1_i103n",
          "cdna": [
            "c.308T>A"
          ],
          "longestTranscript": "NM_002755.3"
        }
      ],
      "sources": [
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "19915144",
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/19915144",
          "year": "",
          "type": "pathway_inferred",
          "id": "1"
        }
      ],
      "clinicalSignificance": "resistant",
      "id": "lc-868",
      "includeCondition0": [
        "Malignant neoplastic disease",
        "Neoplasia",
        "Neoplasm of respiratory tract",
        "Neoplasm of respiratory system",
        "Solid tumor"
      ],
      "includeCondition1": [
        "Neoplasm of lung"
      ],
      "uniqueKey": "2720a1247d4c98a6c19d1d05e4f1080f",
      "prevalence": [
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER MAX"
        },
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER AVG"
        }
      ],
      "regulatoryBodyApproved": False,
      "version": 1,
      "includeMutation1": [
        "MAP2K1 I103N"
      ],
      "includeMutation0": [
        "MAP2K1 Pkinase domain",
        "MAP2K1 exon 3 mutation",
        "MEKi resistance mutations"
      ],
      "regulatoryBody": "FDA",
      "direction": "supports",
      "ampcap": "2D",
      "ast": {
        "operator": "&&",
        "right": {
          "raw": "\"MAP2K1 I103N\"",
          "type": "Literal",
          "value": "MAP2K1 I103N"
        },
        "type": "LogicalExpression",
        "left": {
          "raw": "\"Neoplasm of lung\"",
          "type": "Literal",
          "value": "Neoplasm of lung"
        }
      },
      "tier": "4",
      "tierExplanation": [
        {
          "tier": "1",
          "step": 1,
          "message": "FDA Approved",
          "success": False
        },
        {
          "tier": "1",
          "step": 2,
          "message": "No guideline established",
          "success": False
        },
        {
          "tier": "2",
          "step": 3,
          "message": "Source (trial, case_study, expert) found",
          "success": False
        },
        {
          "tier": "3",
          "step": 4,
          "message": "Source (preclinical, institutional_study) found",
          "success": False
        },
        {
          "tier": "4",
          "step": 5,
          "message": "Source (pathway_inferred) found",
          "success": True
        }
      ],
      "mvld": "4",
      "tags": [
        {
          "priority": 1,
          "term": "Neoplasm of lung",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "custom": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "Neoplasm of lungCONDITIONinclude"
        },
        {
          "priority": 1,
          "term": "MAP2K1 I103N",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "MAP2K1 I103NMUTATIONinclude",
          "custom": True,
          "facet": "MUTATION",
          "valid": True
        },
        {
          "priority": 0,
          "term": "MAP2K1",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "GENE",
          "generatedByTerm": "MAP2K1 I103N"
        },
        {
          "priority": 0,
          "term": "MAP2K1 Pkinase domain",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "MUTATION",
          "generatedByTerm": "MAP2K1 I103N"
        },
        {
          "priority": 0,
          "term": "MAP2K1 exon 3 mutation",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "MUTATION",
          "generatedByTerm": "MAP2K1 I103N"
        },
        {
          "priority": 0,
          "term": "MEKi resistance mutations",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "MUTATION",
          "generatedByTerm": "MAP2K1 I103N"
        },
        {
          "priority": 0,
          "term": "Malignant neoplastic disease",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of lung"
        },
        {
          "priority": 0,
          "term": "Neoplasia",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of lung"
        },
        {
          "priority": 0,
          "term": "Neoplasm of respiratory tract",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of lung"
        },
        {
          "priority": 0,
          "term": "Neoplasm of respiratory system",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of lung"
        },
        {
          "priority": 0,
          "term": "Solid tumor",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of lung"
        },
        {
          "priority": 0,
          "term": "Lung",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "SITE",
          "generatedByTerm": "Neoplasm of lung"
        }
      ],
      "customer": "MolecularMatch",
      "biomarkerClass": "predictive",
      "classifications": [
        {
          "name": "MAP2K1 I103N",
          "classification": "informative"
        }
      ],
      "therapeuticContext": [
        {
          "facet": "DRUG",
          "suppress": False,
          "valid": True,
          "name": "Mek-162"
        }
      ],
      "includeDrug1": [
        "Mek-162"
      ],
      "sixtier": "5",
      "narrative": "MAP2K1 I103N confers resistance to Mek-162 in patients with Neoplasm of lung",
      "expression": "\"Neoplasm of lung\" && \"MAP2K1 I103N\"",
      "includeGene0": [
        "MAP2K1"
      ]
    }


EVIDENCE4 = {
      "criteriaUnmet": [
        {
          "priority": 1,
          "term": "Wild-Type TP53",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "TP53 WILD TYPEGENEinclude",
          "facet": "GENE",
          "valid": True
        },
        {
          "priority": 1,
          "term": "Malignant neoplastic disease",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "CancerCONDITIONinclude"
        }
      ],
      "prevalence": [],
      "mboost": 0,
      "autoGenerateNarrative": True,
      "mutations": [],
      "civic": "D",
      "sources": [
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "17671205",
          "subType": "cell_line",
          "valid": True,
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/17671205",
          "year": "2007",
          "trustRating": 4,
          "type": "preclinical",
          "id": "0bb0b8fa-da3e-4b96-9544-1b24df91ceb5"
        }
      ],
      "clinicalSignificance": "sensitive",
      "id": "9d3f6588-b38e-4877-80cb-89f052978ef3",
      "includeCondition0": [
        "Neoplasia"
      ],
      "includeCondition1": [
        "Malignant neoplastic disease"
      ],
      "uniqueKey": "c3571925f99e4445cd5ef6778d58e26d",
      "ast": {
        "operator": "&&",
        "right": {
          "raw": "\"Malignant neoplastic disease\"",
          "type": "Literal",
          "value": "Malignant neoplastic disease"
        },
        "type": "LogicalExpression",
        "left": {
          "raw": "\"Wild-Type TP53\"",
          "type": "Literal",
          "value": "Wild-Type TP53"
        }
      },
      "mvld": "3",
      "regulatoryBodyApproved": False,
      "version": 1,
      "regulatoryBody": "FDA",
      "direction": "supports",
      "ampcap": "2D",
      "tags": [
        {
          "priority": 1,
          "term": "Wild-Type TP53",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "TP53 WILD TYPEGENEinclude",
          "facet": "GENE",
          "valid": True
        },
        {
          "priority": 1,
          "term": "Malignant neoplastic disease",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "CancerCONDITIONinclude"
        },
        {
          "priority": 0,
          "term": "Neoplasia",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Malignant neoplastic disease"
        }
      ],
      "tier": "3",
      "tierExplanation": [
        {
          "tier": "1",
          "step": 1,
          "message": "FDA Approved",
          "success": False
        },
        {
          "tier": "1",
          "step": 2,
          "message": "Guideline established",
          "success": False
        },
        {
          "tier": "2",
          "step": 3,
          "message": "Source (trial, case_study, expert) found",
          "success": False
        },
        {
          "tier": "3",
          "step": 4,
          "message": "Source (preclinical, institutional_study) found",
          "success": True
        },
        {
          "tier": "4",
          "step": 5,
          "message": "Source (pathway_inferred) found",
          "success": False
        },
        {
          "tier": "5",
          "step": 6,
          "message": "Source (sequencing) found",
          "success": False
        },
        {
          "tier": "5",
          "step": 7,
          "message": "Unknown Biomarker Class",
          "success": False
        }
      ],
      "institution": [],
      "customer": "CIViC",
      "biomarkerClass": "predictive",
      "classifications": [],
      "therapeuticContext": [
        {
          "facet": "DRUG",
          "suppress": False,
          "valid": True,
          "name": "Nutlin-3a"
        }
      ],
      "external_id": [
        "EID2963"
      ],
      "includeDrug1": [
        "Nutlin-3a"
      ],
      "includeGene1": [
        "Wild-Type TP53"
      ],
      "sixtier": "5",
      "noTherapyAvailable": False,
      "narrative": "Wild-Type TP53 confers sensitivity to Nutlin-3a in patients with Malignant neoplastic disease",
      "expression": "\"Wild-Type TP53\" && \"Malignant neoplastic disease\""
    }

EVIDENCE5 = {
      "criteriaUnmet": [
        {
          "priority": 1,
          "term": "Neoplasm of colorectum",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "custom": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "Neoplasm of colorectumCONDITIONinclude"
        },
        {
          "priority": 1,
          "term": "Cetuximab resistance mutations",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "Cetuximab resistance mutationsMUTATIONinclude",
          "custom": True,
          "facet": "MUTATION",
          "valid": True
        }
      ],
      "civic": "N/A",
      "mboost": 0,
      "autoGenerateNarrative": True,
      "mutations": [
        {
          "name": "Cetuximab resistance mutations",
          "classification": "actionable",
          "mutation_type": [],
          "_src": 1,
          "GRCh38_location": [],
          "sources": [],
          "synonyms": [],
          "parents": [],
          "GRCh37_location": [],
          "geneSymbol": "EGFR",
          "pathology": [],
          "id": "a2a321e17c7d2314bedd9c5d7fc458fb7",
          "cdna": [],
          "description": ""
        }
      ],
      "sources": [
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "20921465",
          "subType": "prospective",
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/20921465",
          "year": "",
          "trialId": "NCT00364013",
          "trialPhase": "",
          "type": "trial",
          "id": "1"
        },
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "20921462",
          "subType": "prospective",
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/20921462",
          "year": "",
          "trialId": "NCT00339183",
          "trialPhase": "",
          "type": "trial",
          "id": "2"
        },
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "17470858",
          "subType": "retrospective",
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/17470858",
          "year": "",
          "trialId": "NCT00113763",
          "trialPhase": "",
          "type": "trial",
          "id": "3"
        },
        {
          "name": "PUBMED",
          "suppress": False,
          "pubId": "19114683",
          "subType": "prospective",
          "link": "https://www.ncbi.nlm.nih.gov/pubmed/19114683",
          "year": "",
          "trialId": "",
          "trialPhase": "",
          "type": "trial",
          "id": "4"
        },
        {
          "name": "",
          "suppress": False,
          "pubId": "",
          "link": "https://www.accessdata.fda.gov/drugsatfda_docs/label/2015/125147s200lbl.pdf",
          "year": "",
          "type": "regulatory",
          "id": "5"
        }
      ],
      "clinicalSignificance": "sensitive",
      "id": "crc-s-172",
      "includeCondition0": [
        "Neoplasm of large intestine",
        "Neoplasm of digestive organ",
        "Neoplasm of colon",
        "Neoplasia",
        "Neoplasm of intra-abdominal organs",
        "Solid tumor",
        "Tumour of gastrointestinal tract",
        "Neoplasm of rectum",
        "Neoplasm of intestinal tract",
        "Malignant neoplastic disease",
        "Neoplasm of digestive tract",
        "Neoplasm of digestive system"
      ],
      "includeCondition1": [
        "Neoplasm of colorectum"
      ],
      "uniqueKey": "1d169fa56adf14de6554e4e05a5fcf08",
      "prevalence": [
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER MAX"
        },
        {
          "count": 0,
          "percent": 0,
          "samples": 0,
          "studyId": "PAN CANCER AVG"
        }
      ],
      "regulatoryBodyApproved": False,
      "version": 1,
      "includeMutation1": [
        "Cetuximab resistance mutations"
      ],
      "regulatoryBody": "FDA",
      "direction": "supports",
      "ampcap": "1B",
      "ast": {
        "operator": "&&",
        "right": {
          "raw": "\"Cetuximab resistance mutations\"",
          "type": "Literal",
          "value": "Cetuximab resistance mutations"
        },
        "type": "LogicalExpression",
        "left": {
          "raw": "\"Neoplasm of colorectum\"",
          "type": "Literal",
          "value": "Neoplasm of colorectum"
        }
      },
      "tier": "2",
      "tierExplanation": [
        {
          "tier": "1",
          "step": 1,
          "message": "FDA Approved",
          "success": False
        },
        {
          "tier": "1",
          "step": 2,
          "message": "No guideline established",
          "success": False
        },
        {
          "tier": "2",
          "step": 3,
          "message": "Source (trial, case_study, expert) found",
          "success": True
        }
      ],
      "mvld": "2",
      "tags": [
        {
          "priority": 1,
          "term": "Neoplasm of colorectum",
          "suppress": False,
          "filterType": "include",
          "primary": True,
          "custom": True,
          "facet": "CONDITION",
          "valid": True,
          "compositeKey": "Neoplasm of colorectumCONDITIONinclude"
        },
        {
          "priority": 1,
          "term": "Cetuximab resistance mutations",
          "suppress": False,
          "filterType": "include",
          "compositeKey": "Cetuximab resistance mutationsMUTATIONinclude",
          "custom": True,
          "facet": "MUTATION",
          "valid": True
        },
        {
          "priority": 0,
          "term": "EGFR",
          "suppress": False,
          "generatedBy": "MUTATION",
          "filterType": "include",
          "custom": False,
          "facet": "GENE",
          "generatedByTerm": "Cetuximab resistance mutations"
        },
        {
          "priority": 0,
          "term": "Neoplasm of large intestine",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of digestive organ",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of colon",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasia",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of intra-abdominal organs",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Solid tumor",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Tumour of gastrointestinal tract",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of rectum",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of intestinal tract",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Malignant neoplastic disease",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of digestive tract",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Neoplasm of digestive system",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "CONDITION",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Entire colon",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "SITE",
          "generatedByTerm": "Neoplasm of colorectum"
        },
        {
          "priority": 0,
          "term": "Rectum",
          "suppress": False,
          "generatedBy": "CONDITION",
          "filterType": "include",
          "custom": False,
          "facet": "SITE",
          "generatedByTerm": "Neoplasm of colorectum"
        }
      ],
      "customer": "MolecularMatch",
      "biomarkerClass": "predictive",
      "classifications": [
        {
          "name": "Cetuximab resistance mutations",
          "classification": "actionable"
        }
      ],
      "therapeuticContext": [
        {
          "facet": "DRUG",
          "suppress": False,
          "valid": True,
          "name": "Panitumumab"
        }
      ],
      "includeDrug1": [
        "Panitumumab"
      ],
      "sixtier": "3",
      "narrative": "Cetuximab resistance mutations confers sensitivity to Panitumumab in patients with Neoplasm of colorectum",
      "expression": "\"Neoplasm of colorectum\" && \"Cetuximab resistance mutations\"",
      "includeGene0": [
        "EGFR"
      ]
    }


def test_convert_RET():
    evidences = list(molecularmatch.convert(EVIDENCE))
    assert evidences
    assert len(evidences) == 1
    evidence = evidences[0]
    assert evidence['genes'] == ['RET']


def test_convert_UGT1A1():
    evidences = list(molecularmatch.convert(EVIDENCE2))
    assert evidences
    assert len(evidences) == 1
    evidence = evidences[0]
    assert evidence['genes'] == ['UGT1A1']


def test_convert_MAP2K1():
    evidences = list(molecularmatch.convert(EVIDENCE3))
    assert evidences
    assert len(evidences) == 1
    evidence = evidences[0]
    assert evidence['genes'] == ['MAP2K1']


def test_convert_TP53():
    evidences = list(molecularmatch.convert(EVIDENCE4))
    assert evidences
    assert len(evidences) == 1
    evidence = evidences[0]
    assert evidence['genes'] == ['TP53']
    assert evidence['features'] == [{'geneSymbol': 'TP53',
                                     'name': 'Wild-Type'}]


def test_convert_EGFR():
    evidences = list(molecularmatch.convert(EVIDENCE5))
    assert evidences
    assert len(evidences) == 1
    evidence = evidences[0]
    assert evidence['genes'] == ['EGFR']
    assert evidence['features'] == [{'biomarker_type': 'unspecified',
                                     'geneSymbol': 'EGFR',
                                     'name': 'Cetuximab resistance mutations'}]
