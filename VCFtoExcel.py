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


def call_to_allele(call, motif_length, ref_repeats):
    """
        Convert called STR to observed allele
    :param call: number of base differences from ref
    :param motif_length: length of repeat motif in bases
    :param ref_repeats: Reference allele number of repeats
    :return: allele value
    """
    call = float(call)
    motif_length = float(motif_length)
    ref_repeats = float(ref_repeats)

    ref_bases = motif_length * ref_repeats
    called_bases = ref_bases + call
    quotient, remainder = divmod(called_bases, motif_length)
    allele = str(int(quotient)) + '.' + str(int(remainder))
    return allele


def get_alleles_coverages(reads_field, motif_len, ref_repeats):
    """
        From a VCF entry of variants and coverage, return a dict[allele] = coverage
    """
    covs = reads_field.split(';')
    allele_coverage = {}
    for c in covs:
        variant, cov = c.split('|')
        allele = call_to_allele(variant, motif_len, ref_repeats)
        allele_coverage[allele] = cov
    return allele_coverage


def read_dip_str_names_gt_covs(path, name_gt_covs_dict):
    """
        Expected input format:
        chr16   86386308        -4|2;0|38;4|356;8|258;12|2      4       8       4       11      D16S539 12      13
        chrom   start   allele|reads    1st call    2nd call    motif len   repeats name    allele 1    allele 2
        Get names and the genotype calls from the autosomal (diploid) files for filtering.
        Return dict[chrom, start] = tuple (name, tuple(genotype by alleles), dict[allele]=coverage )
    """
    with open(path, 'r') as input:
        for line in input:
            if line.startswith('#'):
                continue
            lps = line.strip().split('\t')
            chrom = lps[0]
            start = int(lps[1])
            variants_reads = lps[2]
            name = lps[7]  # don't change the case
            call1 = lps[3]
            call2 = lps[4]
            motif_len = lps[5]
            ref_repeats = lps[6]
            gt_allele1 = call_to_allele(call1, motif_len, ref_repeats)
            gt_allele2 = call_to_allele(call2, motif_len, ref_repeats)
            allele_coverage = get_alleles_coverages(variants_reads, motif_len, ref_repeats)
            name_gt_covs_dict[tuple([chrom, start])] = tuple([name, tuple([gt_allele1, gt_allele2]), allele_coverage])


def read_hap_str_names_gt_covs(path, name_gt_covs_dict):
    """
        Get names and the genotype calls from the sex chrom (haploid) files for filtering.
        chrY    6861231 -8|15;-4|251;-1|7;0|1643;4|19;8|2       0       4       17      DYS570  17
        chrom   start    allele|reads   call    motif len   repeats name    allele
        Return dict[chrom, start] = tuple (name, tuple(genotype by alleles), dict[allele]=coverage )
    """
    with open(path, 'r') as input:
        for line in input:
            if line.startswith('#'):
                continue
            lps = line.strip().split('\t')
            chrom = lps[0]
            start = int(lps[1])
            variants_reads = lps[2]
            name = lps[6]  # don't change the case
            call = lps[3]
            motif_len = lps[4]
            ref_repeats = lps[5]
            gt_allele = call_to_allele(call, motif_len, ref_repeats)
            allele_coverage = get_alleles_coverages(variants_reads, motif_len, ref_repeats)
            name_gt_covs_dict[tuple([chrom, start])] = tuple([name, tuple([gt_allele]), allele_coverage])


def collect_allele_lines(cols, name_gt_covs_dict):
    """
    :param cols: VCF entry as a list of columns
    :param name_dict: associates chrom, start position with a locus name
    :return: a list of strings which are formatted lines to output
    """
    outlines = []
    chrom = cols[0]
    pos = cols[1]
    ref_seq = cols[3]
    alt_seq = cols[4]
    qual = cols[5]
    info = cols[7].split(';')
    sample = cols[9].split(':')

    if (chrom, int(pos)) not in name_gt_covs_dict:
        return outlines

    # genotype should be the actual allele calls and be the same for all output lines for a locus

    name, gt, allele_coverage = name_gt_covs_dict[(chrom, int(pos))]

    motif = info[1].split('=')[1]
    ref_allele = info[3].split('=')[1]
    # convert ref allele to correct numbering e.g. 16.25 for a 4 base motif is 16.1
    if '.' in str(ref_allele):
        ref_allele = call_to_allele(0, len(motif), float(ref_allele))

    ref_length = int(info[4].split('=')[1])

    ref_cov = 0
    if str(float(ref_allele)) in allele_coverage:
        ref_cov = allele_coverage[str(float(ref_allele))]

    alt_seqs = alt_seq.split(',')
    len_altseq = {}
    for alt_seq in alt_seqs:
        if alt_seq == '.':
            len_altseq[float(ref_allele)] = 'REF'
        else:
            q,r = divmod(len(alt_seq), len(motif))
            al = str(q) + '.' + str(r)
            len_altseq[float(al)] = alt_seq

    ordered_alleles = sorted([float(k) for k in allele_coverage.keys()])

    # form a proper looking genotype
    if len(gt) > 1:
        gt = '/'.join(gt)
    else:
        gt = gt[0]

    for allele in ordered_alleles:
        # ['#Chromosome', 'Start', 'ID', 'Motif',
        #       'Reference seq', 'Ref allele', 'Ref cov',
        #       'Alternate seq', 'Alt allele', 'Alt cov',
        #       'Quality', 'Locus Genotype']

        alt_seq = ''
        if float(allele) in len_altseq:
            alt_seq = len_altseq[float(allele)]

        outline = ','.join(map(str, [chrom, pos, name, motif, ref_seq,
                ref_allele, ref_cov, alt_seq, allele, allele_coverage[str(allele)], qual, gt]))
        outlines.append(outline)
    return outlines


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
    #Chromosome', 'Start', 'ID', 'Motif', 'Reference seq', 'Ref allele',
    'Ref cov', 'Alternate seq', 'Alt allele', 'Alt cov', 'Quality', 'Locus genotype'

    Each set of called allele counts gets its own line.

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

    name_gt_covs_dict = {}
    read_dip_str_names_gt_covs(codis_fn, name_gt_covs_dict)
    read_hap_str_names_gt_covs(ystr_fn, name_gt_covs_dict)

    with open(csv_fn, 'w') as csv:
        header = ','.join(['#Chromosome', 'Start', 'ID', 'Motif',
                           'Reference seq', 'Ref allele', 'Ref cov',
                           'Alternate seq as called by LobSTR', 'Alt allele', 'Alt cov',
                           'Quality', 'Locus genotype'])
        csv.write(header + '\n')
        with open(args.vcf, 'r') as vcf:
            for line in vcf:
                if line.startswith('#'):  # header line
                    continue
                cols = line.strip().split('\t')
                allele_lines = collect_allele_lines(cols, name_gt_covs_dict)
                for outline in allele_lines:
                    csv.write(outline + '\n')

if __name__ == "__main__":
    main()