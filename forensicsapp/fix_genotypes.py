#!/usr/bin/env python

import sys

def main():
    """
        Read a VCF file that contains homozygous reference entries
        Mark these as 0/0
    """
    with open(sys.argv[1], 'r') as f:
        for line in f:
            if line.startswith('#'):
                print(line.strip())
                continue
            cols = line.strip().split('\t')
            if cols[-2].startswith('GT:'):
                print(line.strip())
            else:
                cols[-2] = 'GT:' + cols[-2]
                cols[-1] = '0/0:' + cols[-1]
                out_line = '\t'.join(cols)
                print(out_line)

if __name__ == '__main__':
   main()

