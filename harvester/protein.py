import requests
import re
import gzip
from pathlib2 import Path
from Bio import SeqIO


def _load_fasta_records(fh):
    fd = {}
    for record in SeqIO.parse(fh, "fasta"):
        _id = record.id
        fd[_id] = record.seq
    return fd


fasta = {}

FASTA_FILE_DIR = Path('../data/proteins')

for f in Path.glob(FASTA_FILE_DIR, '*.faa.gz'):
    with gzip.open(str(f), 'rt') as fasta_file:
        fasta.update(_load_fasta_records(fasta_file))


gene_symbol_to_id = {}
protein_id_re = re.compile('NP_\d+\.\d+')
protein_name_re = re.compile(r'(?P<start>[A-Z]?\d+)(?:-|_(?P<end>[A-Z]?\d+))?(?P<alt_type>(ins|del|dup|INS|DEL|DUP)*)(?P<alt>[A-Z]+)?')


def parse_components(name_string):
    match = protein_name_re.match(name_string)
    return match.groupdict()


def lookup_from_gene(gene_symbol, ref_start=None, ref_end=None, exclude={}):
    if gene_symbol in gene_symbol_to_id:
        _id = gene_symbol_to_id[gene_symbol]
    else:
        resp = requests.get(
            "http://mygene.info/v3/query?q=symbol%3A{}&species=9606".format(gene_symbol)
        )
        resp.raise_for_status()
        _id = resp.json()['hits'][0]["_id"]
        gene_symbol_to_id[gene_symbol] = _id

    resp = requests.get(
        "https://www.ncbi.nlm.nih.gov/gene/{}?report=gene_table&format=text".format(_id)
    )
    resp.raise_for_status()
    proteins = list()
    for protein_match in protein_id_re.finditer(resp.text):
        protein = str(protein_match.group())
        if protein not in proteins:
            proteins.append(protein)
    p_set = set(proteins)
    for known in [ref_start, ref_end]:
        if known is None:
            continue
        aa = known[0]
        pos = int(known[1:])
        keep = set()
        for p in p_set:
            try:
                ref_aa = fasta[p][pos-1]
            except IndexError:
                continue
            if ref_aa == aa:
                keep.add(p)
        p_set = keep & p_set
    for p in proteins:
        if p in p_set and p not in exclude:
            return p
    assert False


def _test_lookup(gene_symbol, expected_protein_id, **kwargs):
    p = lookup_from_gene(gene_symbol, **kwargs)
    assert p == expected_protein_id, "Expected: {}, Observed: {}".format(expected_protein_id, p)


def _test_parse(name_string, **kwargs):
    components = parse_components(name_string)
    for k, v in kwargs.items():
        assert components[k] == v


if __name__ == '__main__':
    _test_lookup('ERBB2', 'NP_001276865.1')

    _test_parse('V600E', start='V600', alt='E')