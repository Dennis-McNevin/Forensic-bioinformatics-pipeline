#!/usr/bin/env python

import argparse
import os

def read_bed(path):
    """ get entries from BED file for filtering """
    bed_entries = {}
    with open(path, 'r') as input:
        for line in input:
            lps = line.strip().split('\t')
            if len(lps) != 6:
                continue
            chrom = lps[0]
            start = int(lps[1])
            motif = int(lps[3])
            repeats = int(lps[4])
            name = lps[5] # don't change the case
            # use upper case for name matching
            bed_entries[name.upper()] = (chrom, start, motif, repeats, name)
    return bed_entries


def write_strs(out_path, bed_entries, name, alleles_reads):
    with open(out_path, 'a') as outf:
        chrom, start, motif, repeats, true_name = bed_entries[name]
        ref_bases = motif * repeats

        calls = []
        g1 = (0,0,0)  # reads,genotype A
        g2 = (0,0,0)  # reads,genotype B
        for (allele, cov) in alleles_reads:
            if '.' in allele:
                whole, fraction = allele.split('.')
                w = int(whole)
                f = int(fraction)
            else:
                w = int(allele)
                f = 0
            num_bases = (w*motif) - f
            # bases_diff = ref_bases - num_bases  # this line is giving the opposite allele polarity
            bases_diff = num_bases - ref_bases
            calls.append(str(bases_diff) + '|' + cov)
            coverage = int(cov)
            if coverage > g1[0]:
                g2 = g1
                g1 = (coverage, bases_diff, w)
            elif coverage > g2[0]:
                g2 = (coverage, bases_diff, w)

        # let's get sorted calls, just to be on the safe side
        temp_calls = []
        for c in calls:
            call = c.split('|')
            temp_calls.append((int(call[0]), int(call[1])))
        calls = sorted(temp_calls)

        temp_calls = []
        for c in calls:
            call = str(c[0]) + '|' + str(c[1])
            temp_calls.append(call)
        calls = temp_calls

        c = ';'.join(calls)
        if "ystr" in out_path:
            outline = '\t'.join([chrom, str(start), c, str(g1[1]), str(g2[1]), str(motif),
                str(repeats), true_name, str(g1[2])])  # no 2nd genotype in y chroms!
        else:
            outline = '\t'.join([chrom, str(start), c, str(g1[1]), str(g2[1]), str(motif),
                str(repeats), true_name, str(g1[2]), str(g2[2])])
        
        outf.write(outline + '\n')


def get_calls_from_razor(razor_path, codis_bed_entries, ystr_bed_entries, codis_path, ystr_path):
    """
        Read entries from razor file.
        1) Skip if they are not in X_bed_entries
        2) Skip if they have no reads
    """
    with open(razor_path, 'r') as ri:
        current_str = ''
        alleles_reads = []  # list of tuples of (allele, reads)
        for line in ri:
            lps = line.strip().split(':')
            if len(lps) != 5 or lps[4] == '':  # no reads called
                continue
            name = lps[0].upper()
            allele = lps[3]
            reads = lps[4]

            if name not in ystr_bed_entries and name not in codis_bed_entries:
                #print 'Skipping unrecognised STR', name
                continue

            if name != current_str:
                if current_str in codis_bed_entries and alleles_reads:
                    write_strs(codis_path, codis_bed_entries, current_str, alleles_reads)
                elif current_str in ystr_bed_entries and alleles_reads:
                    write_strs(ystr_path, ystr_bed_entries, current_str, alleles_reads)
                alleles_reads = []
                current_str = name

            alleles_reads.append((allele, reads))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--yBED', required=True, help='path to Y-chromosome BED file')
    parser.add_argument('--codisBED', required=True, help='path to CODIS BED file')
    parser.add_argument('--razor', required=True, help='path to STRait Razor rawSTRcallsR1.txt')
    parser.add_argument('--trimmedFQ', required=True, help='path to input trimmed FQ')
    # output path is generated
    args = parser.parse_args()

    codis_bed_entries = read_bed(args.codisBED)
    ystr_bed_entries = read_bed(args.yBED)

    codis_path = args.trimmedFQ.split('trimmed')[0]+'straitrazor.codis.txt'
    ystr_path = args.trimmedFQ.split('trimmed')[0]+'straitrazor.ystr.txt'

    if os.path.exists(codis_path):
        os.remove(codis_path)
    if os.path.exists(ystr_path):
        os.remove(ystr_path)

    get_calls_from_razor(args.razor, codis_bed_entries, ystr_bed_entries,
                         codis_path, ystr_path)

if __name__ == '__main__':
    main()
