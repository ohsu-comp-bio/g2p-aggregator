import jax

molecular_profiles = [
    "APC inact mut KRAS G12D",
    "APC mutant BRAF mutant PIK3CA mutant SMAD4 mutant TP53 mutant",
    "BRAF V600E EGFR amp",
    "BRAF V600E MAP2K1 L115P",
    "BRAF V600E NRAS Q61K NRAS A146T MAP2K1 P387S",
    "BRAF amp BRAF V600X NRAS Q61K",
    "CDKN2A mut MET del exon14 PDGFRA mut SMAD4 Q249H",
    "DNMT3A R882H FLT3 Y599_D600insSTDNEYFYVDFREYEY NPM1 W288fs",
    "EGFR E746_A750del EGFR T790M EGFR L718Q",
    "EGFR exon 19 del MET amp MET D1228V",
    "ERBB2 over exp PIK3CA H1047R SRC over exp",
    "ETV6 - JAK2 JAK2 G831R",
    "FGFR2 E565A FGFR2 K659M FGFR2 N549H FGFR2 N549K FGFR2 V564F FGFR2-ZMYM4",
    "FGFR2 N550K PIK3CA I20M PIK3CA P539R PTEN R130Q PTEN T321fs*23",
    "FGFR3 wild-type FGFR3 dec exp HRAS G12V",
    "FLT3 exon 14 ins FLT3 D835N",
    "FLT3 exon 14 ins FLT3 F691L FLT3 D698N",
    "FLT3 exon 14 ins FLT3 M837G FLT3 S838R FLT3 D839H",
    "JAK2 over exp MPL over exp",
    "KRAS G12D PIK3CA E545K PIK3CA H1047L TP53 wild-type",
    "KRAS G12D PTEN dec exp TP53 R306*",
    "KRAS G13C PIK3CA H1047Y PTEN G143fs*4 PTEN K267fs*9",
    "KRAS mut + TP53 wild-type",
    "MET del exon14 TP53 N30fs*14",
    "NPM1-ALK ALK L1196M ALK D1203N",
]


def _parse(molecular_profile):
    """ dispatch to jax harvester """
    return jax._parse(molecular_profile)


def test_parse_all():
    """ just loop through all test profiles, ensure no exceptions """
    genes = []
    for molecular_profile in molecular_profiles:
        genes.append(_parse(molecular_profile)[0])


def test_parse_fusion():
    """ make sure we handle fusion format """
    genes, tuples = _parse("ETV6 - JAK2")
    assert ['ETV6', 'JAK2'] == genes
    assert tuples == [['ETV6', 'ETV6-JAK2'], ['JAK2', 'ETV6-JAK2']]


def test_parse_simple():
    """ make sure we handle fusion format """
    genes, tuples = _parse("BRAF V600E")
    assert ["BRAF"] == genes
    assert tuples == [["BRAF", "V600E"]]


def test_parse_simple_annotated():
    """ make sure we 'annotations' on gene """
    genes, tuples = _parse("MET del exon14")
    assert ["MET"] == genes
    assert tuples == [["MET", "del", "exon14"]]


def test_parse_compound_annotated():
    """ make sure we 'annotations' on gene and others """
    genes, tuples = _parse("MET del exon14 TP53 N30fs*14")
    assert ['MET', 'TP53'] == genes
    assert tuples == [["MET", "del", "exon14"], ["TP53", "N30fs*14"]]


def test_parse_mixed_annotated_compound():
    """ make sure we handle fusion format """
    genes, tuples = _parse("CDKN2A mut MET del exon14 PDGFRA mut SMAD4 Q249H")
    assert ['CDKN2A', 'MET', 'PDGFRA', 'SMAD4'] == genes
    assert tuples == [["CDKN2A", "mut"],
                      ["MET", "del", "exon14"],
                      ["PDGFRA", "mut"],
                      ["SMAD4", "Q249H"]]


def test_parse_terminate_with_fusion():
    """ make sure we handle fusion format in last tuple"""
    genes, tuples = _parse("FGFR2 E565A FGFR2 K659M FGFR2 N549H FGFR2 N549K FGFR2 V564F FGFR2-ZMYM4")  # NOQA
    assert ['FGFR2', 'ZMYM4'] == genes
    assert tuples == [["FGFR2", "E565A"],
                      ["FGFR2", "K659M"],
                      ["FGFR2", "N549H"],
                      ["FGFR2", "N549K"],
                      ["FGFR2", "V564F"],
                      ['FGFR2', "FGFR2-ZMYM4"],
                      ['ZMYM4', "FGFR2-ZMYM4"],
                      ]


def test_plus_sign():
    """ make sure we handle fusion format in last tuple"""
    genes, tuples = _parse("KRAS mut + TP53 wild-type")  # NOQA
    assert ['KRAS', 'TP53'] == genes
    assert tuples == [["KRAS", "mut"],
                      ["TP53", "wild-type"]]


def test_odd_number():
    """ make sure we handle odd number"""
    genes, tuples = _parse("EML4-ALK ALK C1156Y ALK L1198F")
    assert ['ALK', 'EML4'] == genes
    assert tuples == [["ALK", "C1156Y"],
                      ["ALK", "L1198F"],
                      ["EML4", "EML4-ALK"],
                      ["ALK", "EML4-ALK"],
                      ]


def test_act_mut_fusion():
    genes, tuples = _parse("EML4 - ALK SRC act mut")
    assert ['ALK', 'EML4', 'SRC'] == genes
    assert tuples == [["SRC", "act", "mut"],
                      ["EML4", "EML4-ALK"],
                      ["ALK", "EML4-ALK"],
                      ]


def test_act_amp_fusion():
    genes, tuples = _parse("NPM1-ALK amp")
    print genes, tuples
    assert ['ALK', 'NPM1'] == genes
    assert tuples == [["NPM1", "NPM1-ALK amp"],
                      ["ALK", "NPM1-ALK amp"],
                      ]
