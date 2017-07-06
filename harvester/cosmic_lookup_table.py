"""
Parses CosmicMutantExport TSV to create a lookup table that connects
the following data fields: gene, HGVS genomic and protein change, chrom, start,
end, ref, and alt.
"""

import sys
import re
import argparse
import pandas


class CosmicLookup(object):
    """
    Class that uses lookup table to return relevant information.
    """

    def __init__(self, lookup_table_file):
        self.lookup_table = pandas.read_csv(lookup_table_file, sep="\t")
        self.gene_df_cache = {}

    def get_entries(self, gene, hgvs_p):
        """
        Returns a dataframe of results from filtering on gene and hgvs_p
        """
        """
         filter out
         "FLT3 D835X FLT3 exon 14 ins"
        """
        if gene.islower() or gene.isdigit():
            # return null
            print '*******'
            print 'get_entries', gene, hgvs_p
            print '*******'
            return []
        # Get lookup table.
        if gene in self.gene_df_cache:
            # Found gene-filtered lookup table in cache.
            lt = self.gene_df_cache['gene']
        else:
            # Did not find gene-filtered lookup table in cache. Create it
            # and add it to the cache.
            lt = self.lookup_table
            lt = lt[lt['gene'] == gene]
            self.gene_df_cache['gene'] = lt

        hgvs_p = "p." + hgvs_p
        result = lt[(lt['gene'] == gene) & (lt['hgvs_p'].str.contains(hgvs_p))]
        return result.to_dict(orient='records')

#
# Methods below parse CosmicMutantExport TSV and create the lookup table.
#


def parse_hgvc_c(hgvs_c):
    """
    Parses HGVS like c.4146T>A and returns a dictionary with the keys
    pos, type, ref, alt
    """

    if not hgvs_c.startswith("c.") or "?" in hgvs_c:
        return {}

    parts = re.split(r"([[_\.ACGT]+|[0-9]+|del|ins])", hgvs_c[2:])

    bases = "ATCG"
    pos = ctype = ref = alt = None
    if parts[4] == ">":
        # Substitution.
        pos = parts[1]
        ctype = "sub"
        ref = parts[3]
        alt = parts[5]

    return {
        "pos": pos,
        "type": ctype,
        "ref": ref,
        "alt": alt
    }


def parse_genome_pos(genome_pos):
    """
    Parse genome position in format chrom:start-end and returns the tuple
    chrom, start, end
    """

    if not genome_pos:
        return None, None, None
    chrom, pos = genome_pos.split(":")
    start, end = pos.split("-")
    return chrom, start, end


def print_lookup_table(input_stream):
    """
    Create and print COSMIC lookup table by reading from input_stream and
    outputing corresponding line for the lookup table.
    """
    print "\t".join(["gene", "hgvs_c", "hgvs_p", "build", "chrom", "start", "end", "ref", "alt", "strand"])  # NOQA
    for line in input_stream:
        fields = line.split("\t")
        gene = fields[0]
        hgvs_c, hgvs_p = fields[17:19]
        build, genome_pos, strand = fields[22:25]

        parse_results = parse_hgvc_c(hgvs_c)

        chrom, start, end = parse_genome_pos(genome_pos)
        if bool(parse_results) and parse_results["ref"] and chrom:
            print "\t".join([gene, hgvs_c, hgvs_p, build, chrom, start, end, parse_results["ref"], parse_results["alt"], strand])  # NOQA
        else:
            # TODO: Debugging.
            # print >> sys.stderr, "LINE IGNORED", hgvs_c
            pass


def count_matches(lookup_table_file, gene_hgvsp_file):
    """
    Benchmarking method to count the number of matches found using the lookup
    table together with the gene_hgvsp_file. gene_hgvsp_file has format:

    gene<TAB>HGVS.p short notation

    BRAF    V600E
    EGFR    L861Q
    """
    lookup = CosmicLookup(lookup_table_file)
    total = 0
    matched = 0
    unique_matched = 0
    queried = {}
    report = ''

    for line in open(gene_hgvsp_file):
        # Parse line.
        fields = line.strip().split('\t')
        if len(fields) != 2:
            # Something's not right, so ignore.
            continue
        gene, hgvs_p = fields

        # Lookup table and count matches.
        for protein_change in hgvs_p.split(','):
            hash_entry = "%s-%s" % (gene, protein_change)
            matches = lookup.get_entries(gene, protein_change)
            if len(matches) > 0:
                report = 'MATCHED'
                matched += 1
                if hash_entry not in queried:
                    unique_matched += 1
            else:
                report = 'NO MATCH'

            print "%s %s %s" % (report, gene, protein_change)
            queried[hash_entry] = True
            total += 1

    unique_total = len(queried)
    print unique_matched, unique_total, float(unique_matched)/unique_total
    print matched, total, float(matched)/total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='')
    parser.add_argument('--lookup-file', dest='lookup_file', help='')
    parser.add_argument('--benchmark-file', dest='benchmark_file', help='')

    args = parser.parse_args()
    if args.action == 'create_table':
        print_lookup_table(sys.stdin)
    elif args.action == 'benchmark':
        count_matches(args.lookup_file, args.benchmark_file)
