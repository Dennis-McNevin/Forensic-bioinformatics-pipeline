#!/usr/bin/env python

import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-B', '--Bedfile', required=True, help='SNP or STR BED file')
    parser.add_argument('-P', '--Panelfile', required=True, help='New or existing .pnl file for output')
    parser.add_argument('-p', '--paneltype', choices=['str','ai','ii','pi'],
            required=True, help='The type of panel we are importing')
    args = parser.parse_args()
    
    with open(args.Bedfile, 'r') as input:
        if os.path.exists(args.Panelfile):
            mode='a'
        else:
            mode='w'
        with open(args.Panelfile, mode) as output:
            if mode == 'w':
                header = ['#chr', 'start', 'end', 'rsID/LocusID', 'str/ai/ii/pi',
                          'analytic threshold', 'stochastic threshold',
                          'stutter threshold', 'info (motif length;num repeats)']
                output.write('\t'.join(header) + '\n')
            for line in input:
                if line.lower().startswith('track') or line.lower().startswith('#'):
                    continue
                parts = line.strip().split('\t')
                chrom = parts[0]
                start = parts[1]
                end = parts[2]
                analytic_thresh = '5'
                stochastic_thresh = '10'
                stutter_thresh = '5'
                if args.paneltype == 'str': # lobSTR CODIS/ystr format expected
                    motif_length = parts[3]
                    num_repeats = parts[4]
                    id = parts[5]
                    info = motif_length + ';' + num_repeats
                else: # SNP panel, unique entries from hotspot files
                    id = parts[3]
                    info = ''
                outline = [chrom, start, end, id, args.paneltype, 
                           analytic_thresh, stochastic_thresh,
                           stutter_thresh, info]
                output.write('\t'.join(outline)+'\n')

if __name__ == '__main__':
    main()
