import json
import requests
import os
import mutation_type as mut
import logging
import re
import copy
import gene_enricher
import protein


def _enrich_ensemble(feature, transcript_id, exon, provenance_rule):
    """ get coordinates from ensembl
        curl -s 'http://grch37.rest.ensembl.org/lookup/id/ENST00000275493?expand=1'
        | jq '{start:.start, end:.end, chromosome:.seq_region_name, strand:.strand}'
    """  # NOQA
    headers = {'Content-type': 'application/json'}
    url = 'http://grch37.rest.ensembl.org/lookup/id/{}?expand=1' \
        .format(transcript_id)
    r = requests.get(url, timeout=60, headers=headers)
    transcript = r.json()

    if 'Exon' in transcript:
        exon_ = transcript['Exon'][exon-1]
        feature['chromosome'] = str(exon_['seq_region_name'])
        feature['start'] = int(exon_['start'])
        feature['end'] = int(exon_['end'])
        feature['referenceName'] = 'GRCh37'
        if 'provenance' not in feature:
            feature['provenance'] = []
        feature['provenance'].append(url)
        feature['provenance_rule'] = provenance_rule
    return feature


def _enrich_gene(feature,
                 gene=None,
                 provenance_rule='default'):
    """ description contains a gene, get its location """
    if not gene:
        gene = feature['description']
    parms = 'fields=genomic_pos_hg19'
    url = "http://mygene.info/v3/query?q={}&{}".format(gene, parms)
    r = requests.get(url, timeout=60)
    hit = None
    hits = r.json()
    if 'hits' in hits:
        for a_hit in hits['hits']:
            if 'genomic_pos_hg19' in a_hit:
                hit = a_hit['genomic_pos_hg19']
                break

    if isinstance(hit, list):
        alternatives = hit
        for alternative in alternatives:
            if alternative['chr'] in ['20', '21', '22', '23', '1', '3', '2',
                                      '5', '4', '7', '6', '9', '8', 'Y', 'X',
                                      '11', '10', '13', '12', '15', '14', '17',
                                      '16', '19', '18']:
                hit = alternative
    if hit:
        if 'chr' in hit and 'chromosome' not in feature:
            feature['chromosome'] = str(hit['chr'])
        if 'start' in hit:
            feature['start'] = hit['start']
        if 'end' in hit:
            feature['end'] = hit['end']
        feature['referenceName'] = 'GRCh37'
        if 'provenance' not in feature:
            feature['provenance'] = []
        feature['provenance'].append(url)
        feature['provenance_rule'] = provenance_rule
    return feature


def _enrich_feature(feature,
                    provenance_rule='default'):
    """ description contains a gene + variant, get its location """
    #  curl -s http://myvariant.info/v1/query?q=FLT3%20N676D |
    # jq '.hits[0] |
    # { referenceName: "GRCh37", chromosome: .chrom,
    # start: .hg19.start, end: .hg19.end, ref: .vcf.ref, alt: .vcf.alt  }'
    # {
    #   "referenceName": "GRCh37",
    #   "chromosome": "13",
    #   "start": 28644637,
    #   "end": 28644637,
    #   "ref": "T",
    #   "alt": "A"
    # }
    url = "http://myvariant.info/v1/query?q={}".format(feature['description'])
    r = requests.get(url, timeout=60)
    hits = r.json()
    hit = None
    if 'hits' in hits:
        for a_hit in hits['hits']:
            if 'hg19' in a_hit and 'vcf' in a_hit:
                hit = a_hit
                break
    if hit:
        hg19 = hit.get('hg19')
        vcf = hit.get('vcf')
        if 'ref' in vcf:
            feature['ref'] = vcf['ref']
        if 'alt' in vcf:
            feature['alt'] = vcf['alt']
        if 'chrom' in hit:
            feature['chromosome'] = str(hit['chrom'])
        if 'start' in hg19:
            feature['start'] = hg19['start']
        if 'end' in hg19:
            feature['end'] = hg19['end']
        feature['referenceName'] = 'GRCh37'
        if 'provenance' not in feature:
            feature['provenance'] = []
        feature['provenance'].append(url)
        feature['provenance_rule'] = provenance_rule

        if 'biomarker_type' not in feature:
            if 'cadd' in hit and 'type' in hit['cadd']:
                feature['biomarker_type'] = \
                    mut.norm_biomarker(hit['cadd']['type'])

    return feature


def enrich(feature, feature_association):
    """
    given a feature, decorate it with location
    """
    enriched_features = [feature]

    # rules for protein features
    if feature.get('protein_allele', False):
        components = protein.parse_components(feature['name'])
        for component in ['alt', 'start', 'end']:
            if not feature.get('protein_{}'.format(component), False):
                feature['protein_{}'.format(component)] = components[component]
        if components.get('alt_type', False):
            feature['biomarker_type'] = components['alt_type']
        return enriched_features

    # rules for other features
    try:
        # return if already there
        if feature.get('start', None):
            feature['provenance_rule'] = 'from_source'
            return [feature]

        # make sure it has a name and a description
        if not feature.get('description', None):
            feature['description'] = feature.get('name', None)
        if not feature.get('name', None):
            feature['name'] = feature.get('description', None)

        # we can't normalize things without a description
        if not feature.get('description', None):
            feature['provenance_rule'] = 'missing_description'
            return [feature]


        # apply rules
        description_parts = re.split(' +', feature['description'].strip())
        description_length = len(description_parts)
        source = feature_association['source'] if 'source' in feature_association else None
        exonMatch = re.match(r'.* Exon ([0-9]*) .*', feature['name'], re.M|re.I)

        def _is_gene(symbols):
            """ return true if all symbols exist"""
            for symbol in symbols:
                try:
                    gene = gene_enricher.get_gene(symbol)
                except ValueError:
                    return False
            return True

        enriched_features = []
        if (
            not _is_gene([description_parts[0]]) and
            len(description_parts[0].split('-')) == 2 and
            _is_gene(description_parts[0].split('-'))
           ):
            fusion_donor, fusion_acceptor = description_parts[0].split('-')
            feature_fusion_donor = _enrich_gene(copy.deepcopy(feature), fusion_donor, provenance_rule='is_fusion_donor')  # NOQA
            feature_fusion_donor['geneSymbol'] = fusion_donor
            enriched_features.append(feature_fusion_donor)
            feature_fusion_acceptor = _enrich_gene(copy.deepcopy(feature), fusion_acceptor, provenance_rule='is_fusion_acceptor')  # NOQA
            feature_fusion_acceptor['geneSymbol'] = fusion_acceptor
            enriched_features.append(feature_fusion_acceptor)
        elif description_length == 1:
            feature = _enrich_gene(feature, provenance_rule='gene_only')
            enriched_features.append(feature)
        elif ('oncokb' == source and
              'clinical' in feature_association['oncokb'] and
              exonMatch and
              'Isoform' in feature_association['oncokb']['clinical']):
            isoform = feature_association['oncokb']['clinical']['Isoform']
            feature = _enrich_ensemble(feature,
                                       transcript_id=isoform,
                                       exon=int(exonMatch.group(1)),
                                       provenance_rule='is_oncokb_exon')
            enriched_features.append(feature)

        elif ('deletion' in feature['description'].lower() or
              'del ' in feature['description'].lower()):
            feature = _enrich_gene(feature, description_parts[0],
                                   provenance_rule='is_deletion')
            enriched_features.append(feature)

        elif ('amplification' in feature['description'].lower() or
              'amp ' in feature['description'].lower()):
            feature = _enrich_gene(feature, description_parts[0],
                                   provenance_rule='is_amplification')
            enriched_features.append(feature)
        elif 'loss' in feature['description'].lower():
            feature = _enrich_gene(feature, description_parts[0],
                                   provenance_rule='is_loss')
            enriched_features.append(feature)
        elif 'mutation' in feature['description'].lower():
            feature = _enrich_gene(feature, description_parts[0],
                                   provenance_rule='is_mutation')
            enriched_features.append(feature)
        elif 'inact mut' in feature['description'].lower():
            feature = _enrich_gene(feature, description_parts[0],
                                   provenance_rule='is_inact_mut')
            enriched_features.append(feature)
        else:
            feature = _enrich_feature(feature,
                                      provenance_rule='default_feature')
            enriched_features.append(feature)
    except Exception as e:
        logging.error(feature, exc_info=1)

    return enriched_features
