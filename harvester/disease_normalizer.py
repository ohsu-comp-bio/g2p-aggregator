import requests
import urllib
import logging
import re


disease_alias = {}
with open('disease_alias.tsv', "r") as f:
    for line in f:
        if line.startswith("#"):
            continue
        inline_list = line.rstrip().split('\t')
        disease_alias[inline_list[0]] = inline_list[1]


def normalize_ebi(name):
    """ call ebi & retrieve """
    name = urllib.quote_plus(project_lookup(name))
    url = 'https://www.ebi.ac.uk/ols/api/search?q={}&groupField=iri&exact=on&start=0&ontology=doid'.format(name)  # NOQA
    # .response
    """
    {
      "numFound": 1,
      "start": 0,
      "docs": [
        {
          "id": "doid:http://purl.obolibrary.org/obo/DOID_1909",
          "iri": "http://purl.obolibrary.org/obo/DOID_1909",
          "short_form": "DOID_1909",
          "obo_id": "DOID:1909",
          "label": "melanoma",
          "description": [
            "A cell type cancer that has_material_basis_in abnormally proliferating cells derives_from melanocytes which are found in skin, the bowel and the eye."
          ],
          "ontology_name": "doid",
          "ontology_prefix": "DOID",
          "type": "class",
          "is_defining_ontology": true
        }
      ]
    }

    """  # NOQA

    r = requests.get(url, timeout=20)
    rsp = r.json()
    if 'response' not in rsp:
        return []
    response = rsp['response']
    numFound = response['numFound']
    if numFound == 0:
        return []
    doc = response['docs'][0]
    term = {'ontology_term': doc['obo_id'].encode('utf8'),
            'label': doc['label'].encode('utf8')}

    family = get_family(doc['obo_id'])
    if family:
        term['family'] = family

    return [term]


def get_family(doid):
    # get the hierarchy
    try:
        url = 'http://disease-ontology.org/query_tree?search=True&node={}'.format(doid)  # NOQA
        r = requests.get(url, timeout=20)
        rsp = r.json()
        return get_hierarchy_family(get_hierarchy(rsp[0], []))['text']
    except Exception as e:
        logging.error('{} {} {}'.format(url, r, e))
        return None


def get_hierarchy(node, hierarchy_list):
    if (
        node.get('iconCls', '') == 'search-select-icon' or
        node.get('expanded', False)
    ):
        hierarchy_list.append({'text': node['text'], 'id': node['id']})
        for n in node.get('children', []):
            get_hierarchy(n, hierarchy_list)
    return hierarchy_list


def print_hierarchy(hierarchy_list, indent=0):
    for node in hierarchy_list:
        print ''.ljust(indent), node['text'], node['id']
        indent = indent + 2


def get_hierarchy_family(_a):
    midpoint = int(len(_a)/2) + 1
    return _a[midpoint]


def normalize(name):
    try:
        name = name.encode('utf8')
    except Exception as e:
        pass
    try:
        diseases = []
        if name:
            names = re.split("[\,;]+", name)
            for name_part in names:
                normalized_diseases = normalize_ebi(name_part)
                diseases = diseases + normalized_diseases
        return diseases
    except Exception as e:
        logging.warning("Could not normalize {}".format(name))
        raise e
        return []


def normalize_feature_association(feature_association):
    """ given the 'final' g2p feature_association,
    update it with normalized diseases """
    # nothing to read?, return
    association = feature_association['association']
    if 'phenotype' not in association:
        return
    diseases = normalize(association['phenotype']['description'])
    if len(diseases) == 0:
        feature_association['dev_tags'].append('no-doid')
        return
    # TODO we are only looking for exact match of one disease right now
    association['phenotype']['type'] = {
        'id': diseases[0]['ontology_term'],
        'term': diseases[0]['label']
    }
    if 'family' in diseases[0]:
        association['phenotype']['family'] = diseases[0]['family']

    association['phenotype']['description'] = diseases[0]['label']


def project_lookup(name):

    # disease_alias['Neoplasm of breast'] = 'Breast Cancer'
    # disease_alias['MM - Malignant melanoma of skin'] = 'skin melanoma'
    # disease_alias['Carcinoma of ovary'] = 'ovarian cancer'
    # disease_alias['PTC - Papillary thyroid carcinoma'] = 'papillary thyroid carcinoma'
    # disease_alias['CA - Carcinoma of breast'] = 'Breast Cancer'
    # disease_alias['CML - Chronic myeloid leukaemia'] = 'chronic myeloid leukemia'
    # disease_alias['Malignant tumor of breast'] = 'Breast Cancer'
    #
    # disease_alias['Malignant peripheral nerve sheat tumor'] = 'malignant peripheral nerve sheath tumor'
    # disease_alias['Lung squamous cell'] = 'lung squamous cell carcinoma'
    #
    # disease_alias['Neoplasm of lung'] = 'lung adenocarcinoma'
    # disease_alias['Billiary tract'] = 'biliary tract neoplasm'
    # disease_alias['Lung squamous cell'] = 'lung squamous cell carcinoma'
    # disease_alias['Neoplasm of digestive system'] = 'gastrointestinal system cancer'
    # disease_alias['Gastrointestinal stromal'] = 'Gastrointestinal stromal tumor'
    # disease_alias['B Lymphoblastic Leukemia/Lymphoma'] = 'B-cell adult acute lymphocytic leukemia'
    # disease_alias['Neoplasm of colon'] = 'Neoplasm of the colon'
    # disease_alias['T Lymphoblastic Leukemia/Lymphoma'] = 'acute T cell leukemia'
    # disease_alias['Advanced Solid Tumor'] = 'Cancer'
    # disease_alias['non-small cell lung cancer'] = 'non-small cell lung carcinoma'
    # disease_alias['Non-small cell lung'] = 'non-small cell lung carcinoma'
    # disease_alias['All Tumors'] = 'Cancer'
    # disease_alias['All Solid Tumors'] = 'Cancer'
    # disease_alias['Solid tumor'] = 'Cancer'
    # disease_alias['Solid tumors'] = 'Cancer'
    # disease_alias['Ovary'] = 'ovarian cancer'
    # disease_alias['Any cancer type'] = 'Cancer'
    # disease_alias['Thyroid'] = 'Thyroid cancer'
    # disease_alias['Malignant neoplastic disease'] = 'Cancer'
    # disease_alias['ACC'] = 'Adrenocortical Carcinoma'
    # disease_alias['ALL'] = 'Acute Lymphoblastic Leukemia'
    # disease_alias['AML'] = 'Acute Myeloid Leukemia'
    # disease_alias['APML'] = 'Acute Promyelocytic Leukaemia'
    # disease_alias['BCC'] = 'Basal cell carcinoma'
    # disease_alias['BCL'] = 'B-Cell Lymphoma'
    # disease_alias['BLCA'] = 'Bladder Cancer'
    # disease_alias['BOCA'] = 'Bone Cancer'
    # disease_alias['BRCA'] = 'Breast Cancer'
    # disease_alias['BTCA'] = 'Biliary Tract Cancer'
    # disease_alias['BT'] = 'Biliary Tract Cancer'
    # disease_alias['CCSK'] = 'Clear Cell Sarcoma of the Kidney'
    # disease_alias['CER'] = 'cervical cancer'
    # disease_alias['CESC'] = 'Cervical Squamous Cell Carcinoma'
    # disease_alias['CHOL'] = 'Cholangiocarcinoma'
    # disease_alias['CH'] = 'Cholangiocarcinoma'
    # disease_alias['CLLE'] = 'Chronic Lymphocytic Leukemia'
    # disease_alias['CMDI'] = 'Chronic Myeloid Disorders'
    # disease_alias['CNS'] = 'central nervous system cancer'
    # disease_alias['COAD'] = 'Colon Adenocarcinoma'
    # disease_alias['COCA'] = 'Colorectal Cancer'
    # disease_alias['COREAD'] = 'Colorectal adenocarcinoma'
    # disease_alias['DLBC'] = 'Lymphoid Neoplasm Diffuse Large B-cell Lymphoma'
    # disease_alias['Diffuse Large B Cell Lymphoma'] = 'diffuse large B-cell lymphoma'
    # disease_alias['EOPC'] = 'Early Onset Prostate Cancer'
    # disease_alias['ESAD'] = 'Esophageal Adenocarcinoma'
    # disease_alias['ESCA'] = 'Esophageal Cancer'
    # disease_alias['GACA'] = 'Gastric Cancer'
    # disease_alias['GBM'] = 'Glioblastoma Multiforme'
    # disease_alias['HNSC'] = 'Head and Neck Squamous Cell Carcinoma'
    # disease_alias['KICH'] = 'Kidney Chromophobe'
    # disease_alias['KIRC'] = 'Kidney Renal Clear Cell Carcinoma'
    # disease_alias['KIRP'] = 'Kidney Renal Papillary Cell Carcinoma'
    # disease_alias['L'] = 'Lung Cancer'
    # disease_alias['LAML'] = 'Acute Myeloid Leukemia'
    # disease_alias['LGG'] = 'Brain Lower Grade Glioma'
    # disease_alias['LIAD'] = 'Benign Liver Tumour'
    # disease_alias['LICA'] = 'Liver Cancer'
    # disease_alias['LIHC'] = 'Liver Hepatocellular Carcinoma'
    # disease_alias['LIHM'] = 'Liver Cancer'
    # disease_alias['LINC'] = 'Liver Cancer'
    # disease_alias['LIRI'] = 'Liver Cancer'
    # disease_alias['LMS'] = 'Soft tissue cancer'
    # disease_alias['LUAD'] = 'Lung Adenocarcinoma'
    # disease_alias['LUSC'] = 'Lung Cancer'
    # disease_alias['MALY'] = 'Malignant Lymphoma'
    # disease_alias['MELA'] = 'Skin Cancer'
    # disease_alias['MESO'] = 'Mesothelioma'
    # disease_alias['NBL'] = 'Neuroblastoma'
    # disease_alias['NKTL'] = 'Blood Cancer'
    # disease_alias['ORCA'] = 'Oral Cancer'
    # disease_alias['OS'] = 'Osteosarcoma'
    # disease_alias['OV'] = 'Ovarian Cancer'
    # disease_alias['PAAD'] = 'Pancreatic Cancer'
    # disease_alias['PACA'] = 'Pancreatic Cancer'
    # disease_alias['PAEN'] = 'Pancreatic Endocrine Neoplasms'
    # disease_alias['PBCA'] = 'Pediatric Brain Cancer'
    # disease_alias['PCPG'] = 'Pheochromocytoma and Paraganglioma'
    # disease_alias['PRAD'] = 'Prostate Cancer'
    # disease_alias['READ'] = 'Rectum Adenocarcinoma'
    # disease_alias['Neoplasm of rectum'] = 'rectum cancer'
    # disease_alias['RECA'] = 'Renal Cancer'
    # disease_alias['RT'] = 'Rhabdoid Tumor'
    # disease_alias['Neoplasm of respiratory tract'] = 'respiratory system cancer'
    # disease_alias['Neoplasm of respiratory system'] = 'respiratory system cancer'
    # disease_alias['SARC'] = 'Sarcoma'
    # disease_alias['salivary duct carcinoma'] = 'salivary gland carcinoma'
    # disease_alias['SKCA'] = 'Skin Adenocarcinoma'
    # disease_alias['SKCM'] = 'Skin Cutaneous Melanoma'
    # disease_alias['STAD'] = 'Stomach Adenocarcinoma'
    # disease_alias['TGCT'] = 'Testicular Germ Cell Tumors'
    # disease_alias['THCA'] = 'Thyroid Cancer'
    # disease_alias['TH'] = 'Thyroid Cancer'
    # disease_alias['THYM'] = 'Thymoma'
    # disease_alias['UCEC'] = 'Uterine Corpus Endometrial Carcinoma'
    # disease_alias['UCS'] = 'Uterine Carcinosarcoma'
    # disease_alias['UC'] = 'bladder urachal urothelial carcinoma'
    # disease_alias['urothelial carcinoma'] = 'bladder urachal urothelial carcinoma'
    # disease_alias['UTCA'] = 'Uterine Cancer'
    # disease_alias['UVM'] = 'Uveal Melanoma'
    # disease_alias['WT'] = 'Wilms Tumor'
    # disease_alias['Neoplasm of colorectum'] = 'rectal neoplasm'
    disease = disease_alias.get(name)
    if not disease == name and disease:
        logging.warning('renamed {} to {}'.format(name, disease))
    if not disease:
        disease = name
    return disease
