# -*- coding: utf-8 -*-

# import each of your python pipeline modules ...

import startup
import run_tovcf
import run_lobstr
import run_strrazor
import run_bamToFQ

main = startup.main
sstime = startup.sstime

import os
srcdir = "forensicsapp"

# tuples specify Pages in the Application
# 1. Text to appear in the Tab in the application
# 2. configuration filename for the pipeline
# 3. function to call when "Run" is clicked

pages = [
        ('to VCF', os.path.join(srcdir, 'tovcf.cfg'), run_tovcf.tovcf, None),
        ('Find SNPs', os.path.join(srcdir, 'findsnp.cfg'), run_tovcf.tovcf, [
          ('Trimmomatic', 'forensicsapp/snp_trimmo.cfg'),
          ('BWA', 'forensicsapp/bwa.cfg'),
          ('Mpileup', 'forensicsapp/mpileup.cfg'),
        ]),
        ('LobSTR', os.path.join(srcdir, 'lobstr.cfg'), run_lobstr.lobstr, None),
        ('STRait Razor', os.path.join(srcdir, 'strrazor.cfg'), run_strrazor.strrazor, None),
        ('BAM To FASTQ', os.path.join(srcdir, 'bamToFQ.cfg'), run_bamToFQ.bamToFQ, None),
    ]
