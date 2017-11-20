#!/usr/bin/env python

import argparse

def main():
    """
        Read _snps.txt file and produce simple csv
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('snps', help='Path to snps.txt file')
    parser.add_argument('csv', help='Path to output csv file')
    args = parser.parse_args()

    with open(args.csv, 'w') as out:
        rsid_outlines = []
        with open(args.snps, 'r') as f:
            out.write(','.join(['Refseq ID', 'Ref Nuc', 'Genotype', 'Coverage',
                    'A Reads', 'C Reads', 'G Reads', 'T Reads', 'Major Allele %']) + '\n')
            for line in f:
                if 'indel' in line:
                    continue  # explicitly ignore indels
                if line == '':
                    continue
                cols = line.strip().split('\t')
                id = cols[3]
                ref_nuc = cols[12].upper()
                alt_nuc = cols[13].upper()
                # again, check for indels
                if len(ref_nuc) > 1 or len(alt_nuc) > 1:
                    continue
                if alt_nuc == '.':
                    alt_nuc = ref_nuc

                dp4 = map(int, [d.split('=')[1] for d in \
                        cols[16].split(';') if 'DP4' in d][0].split(','))

                cov = sum(dp4)
                reads_A, reads_C, reads_G, reads_T = 0, 0, 0, 0
                reads_ref = dp4[0] + dp4[1]
                reads_alt = dp4[2] + dp4[3]
                if ref_nuc == 'A':
                    if alt_nuc == 'C':
                        reads_A, reads_C = reads_ref, reads_alt
                    elif alt_nuc == 'G':
                        reads_A, reads_G = reads_ref, reads_alt
                    elif alt_nuc == 'T':
                        reads_A, reads_T = reads_ref, reads_alt
                    else:
                        reads_A = reads_ref
                elif ref_nuc == 'C':
                    if alt_nuc == 'A':
                        reads_C, reads_A = reads_ref, reads_alt
                    elif alt_nuc == 'G':
                        reads_C, reads_G = reads_ref, reads_alt
                    elif alt_nuc == 'T':
                        reads_C, reads_T = reads_ref, reads_alt
                    else:
                        reads_C = reads_ref
                elif ref_nuc == 'G':
                    if alt_nuc == 'A':
                        reads_G, reads_A = reads_ref, reads_alt
                    elif alt_nuc == 'C':
                        reads_G, reads_C = reads_ref, reads_alt
                    elif alt_nuc == 'T':
                        reads_G, reads_T = reads_ref, reads_alt
                    else:
                        reads_G = reads_ref
                elif ref_nuc == 'T':
                    if alt_nuc == 'A':
                        reads_T, reads_A = reads_ref, reads_alt
                    elif alt_nuc == 'C':
                        reads_T, reads_C = reads_ref, reads_alt
                    elif alt_nuc == 'G':
                        reads_T, reads_G = reads_ref, reads_alt
                    else:
                        reads_T = reads_ref
                else:
                    print(ref_nuc, alt_nuc, dp4)

                gt = cols[18].split(':')[0]
                if '.' in gt or gt == '0/0':
                    out_gt = ref_nuc + ref_nuc
                elif gt == '1/1':
                    out_gt = alt_nuc + alt_nuc
                else:
                    out_gt = ref_nuc + alt_nuc
                if reads_ref >= reads_alt:
                    maj_allele_pcnt = (float(reads_ref) / (reads_ref + reads_alt)) * 100
                else:
                    maj_allele_pcnt = (float(reads_alt) / (reads_ref + reads_alt)) * 100

                outcols = [id, ref_nuc, out_gt, cov, reads_A, reads_C, 
                        reads_G, reads_T, maj_allele_pcnt]
                outline = ','.join(map(str, outcols)) + '\n'
                rsid_outlines.append( (int(id.lstrip('rs')) , outline) )
        for rsid, ol in sorted(rsid_outlines):
            out.write(ol)


if __name__ == '__main__':
    main()
