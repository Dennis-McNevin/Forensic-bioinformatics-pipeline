#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    MPS Forensics converter of VCF files to Excel-pretty format
    author: Cameron Jack, ANU Bioinformatics Consultancy,
        John Curtin School of Medical Research,
        Australian National University
    3-JUL-2016

    This program reads VCF (Variant Call Format) files and writes them
    back out to a csv format file with a consistent header and no
    compound columns.

    Only supports LobSTR at this time as it also uses the CODIS and Y-chr
    parsed results.
"""

from __future__ import print_function
import argparse

__version__ = "0.1-b2"
__progname__ = "MPS Forensics"


def read_str_names(path, name_dict, name_col):
    """
        Get names from the CODIS and Ystr files for filtering.
        Requires the column number for the names
        Add to name_dict and return
    """
    with open(path, 'r') as input:
        for line in input:
            lps = line.strip().split('\t')
            chrom = lps[0]
            start = int(lps[1])
            name = lps[name_col]  # don't change the case
            name_dict[(chrom, start)] = name


def main():
    """
    VCF format: tab separated
    #CHROM POS ID REF ALT QUAL FILTER INFO FORMAT NA00001

    From LobSTR:
    chr1    230905351       .       ACACACACACAC    .       2100.41 .
    END=230905362;MOTIF=AC;NS=1;REF=6;RL=12;RU=AC;VT=STR
    GT:ALLREADS:AML:DISTENDS:DP:GB:PL:Q:SB:STITCH
    0/0:-12|22;0|7:0/0:21.8571:29:0/0:0:0:65:0

    CODIS:
    chr11   2192318 -4|32;0|6;4|49  -4      4       4       7       TH01
     6       8

    Y-str:
    chrY    3640831 -4|2;0|2        0       4       12      DYS505  12

    CSV format: comma separated
    #CHROM POS ID REF ALT QUAL
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--caller', choices=['lobstr'],
            default='lobstr', help='Name of software that produced the ' +
            'VCF file')
    parser.add_argument('vcf', help='Path to input VCF')
    args = parser.parse_args()

    codis_fn = args.vcf.replace('.vcf', '.codis.txt')
    ystr_fn = args.vcf.replace('.vcf', '.ystr.txt')
    csv_fn = args.vcf.replace('.vcf', '_excel.csv')

    name_dict = {}
    read_str_names(codis_fn, name_dict, 7)
    read_str_names(ystr_fn, name_dict, 6)

    with open(csv_fn, 'w') as csv:
        header = ','.join(['#Chromosome', 'Start', 'ID', 'Motif',
                           'Reference seq', 'Ref allele', 'Ref cov',
                           'Alternate seq', 'Alt allele', 'Alt cov',
                           'Quality', 'Locus genotype'])
        csv.write(header + '\n')
        with open(args.vcf, 'r') as vcf:
            for line in vcf:
                if line.startswith('#'):  # header line
                    continue
                cols = line.strip().split('\t')
                chrom = cols[0]
                pos = cols[1]
                ref = cols[3]
                alt = cols[4]
                qual = cols[5]
                info = cols[7].split(';')
                sample = cols[9].split(':')

                if (chrom, int(pos)) not in name_dict:
                    continue

                name = name_dict[(chrom, int(pos))]
                alts = alt.split(',')
                gt = 'Locus ' + sample[0]  # genotype
                cov_field = sample[1]  # get coverages
                covs = cov_field.split(';')
                reps_covs = []
                ref_cov = 0
                for c in covs:
                    rep, cov = c.split('|')
                    if rep == '0':
                        ref_cov = cov
                    else:
                        reps_covs.append((rep,cov))

                motif = info[1].split('=')[1]
                ref_al = info[3].split('=')[1]
                ref_length = int(info[4].split('=')[1])

                for a, rc in zip(alts, reps_covs):
                    # ['#Chromosome', 'Start', 'ID', 'Motif',
                    #       'Reference seq', 'Ref allele', 'Ref cov',
                    #       'Alternate seq', 'Alt allele', 'Alt cov',
                    #       'Quality', 'Locus Genotype']

                    # calculate the true allele value
                    quotient, remainder = divmod(ref_length+int(rc[0]),
                                                 len(motif))
                    allele = str(quotient) + '.' + str(remainder)
                    outline = ','.join(map(str, [chrom, pos, name, motif, ref,
                            ref_al, ref_cov, a, allele, rc[1], qual, gt]))
                    csv.write(outline + '\n')

if __name__ == "__main__":
    main()