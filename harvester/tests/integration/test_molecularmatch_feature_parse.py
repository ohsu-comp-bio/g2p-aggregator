import molecularmatch

mutations = [
    "Wild-Type TP53",
    "Wild-Type RB1",
    "MET c.3028+2T>G",
    "TRIM24-NTRK2",
    "RET C634 Mutations",
    "9p24.1 amplification"
]


def _parse(mutation):
    """ dispatch to molecularmatch harvester """
    return molecularmatch._parse(mutation)


def test_parse_all():
    """ just loop through all test profiles, ensure no exceptions """
    genes = []
    for mutation in mutations:
        genes.append(_parse(mutation)[0])


def test_wild_type():
    """ make sure we handle weird wild type format """
    genes, tuples = _parse("Wild-Type TP53")
    assert ['TP53'] == genes
    assert tuples == [['TP53', 'Wild-Type']]


def test_MET():
    """ make sure we handle fusion format """
    genes, tuples = _parse("MET c.3028+2T>G")
    assert ['MET'] == genes
    assert tuples == [['MET', 'c.3028+2T>G']]


def test_fusion():
    """ make sure we handle fusion format """
    genes, tuples = _parse("TRIM24-NTRK2")
    assert ['NTRK2', 'TRIM24'] == genes
    assert tuples == [['NTRK2'], ['TRIM24']]


def test_amplification():
    """ make sure we handle amplification format """
    genes, tuples = _parse("9p24.1 amplification")
    assert ['9p24.1'] == genes
    assert tuples == [['9p24.1', 'amplification']]
