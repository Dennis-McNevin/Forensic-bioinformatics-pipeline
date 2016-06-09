#!/usr/bin/env python

"""
Mpileup and Freebayes pipeline

Authors: Cameron Jack & Bob Buckley
ANU Bioinformatics Consultancy,
John Curtin School of Medical Research,
Australian National University
18/5/2016

This code is part os the Forensics project.
It uses mpileup or freebayes to get a VCF file ...
"""


#import os
#import time
import modpipe as px
import modcommon as com

import location
loc = location.location

#files = [
#           "samtools", "bcftools", "bwa",
#           "freebayes",
#           "snp_convert.sh", 
#           "human.fa",
#        ]
#
#home, results = com.forensicsenv

#results = loc['results']
#default_reference = loc['human.fa']
# freebayes=os.path.join(home, 'bin', "freebayes")
# default_reference = os.path.join(home, 'lib', 'ref', 'human.fa')

def tovcf(itrfce, progress=None):
    """
        Pipeline for running mpileup (or freebayes)

        Define a hardcoded pipeline that gets its optional command strings
        from Bob's interface code.

        itrfce is a dictionary of dictionaries, with each top level key
        being a pipeline stage and each second level key being the
        argument and the value being the value of said argument.

        progress is an optional progress bar object we can update

        It calls the following programs (expected on $PATH somewhere):
            samtools
            bcftools
            bwa
    """
    global loc

    for sect in ['Shared', 'mpileup']: # BWA? Trimmomatic?
        if not sect in itrfce:
            print sect, "is not present in the interface dictionary :("
            return False

    tovcfprog = itrfce['Shared']['tovcf']
    assert tovcfprog in ['mpileup', 'freebayes']

    trim_fq, bn, cmds, pipedir, logger = com.prepare(itrfce, tovcfprog, progress)
    threads = itrfce['Shared']['threads']
    ref = itrfce['Shared']['R']
    if not ref:
        ref = loc['human.fa']
    assert ref

    # Stage 4 BWA
    logger.info ('Preparing BWA alignment')
    sam_fn = bn + '.sam'
    cmds.append((
                 [loc['bwa'], 'mem', '-t', threads, ref] + trim_fq + [ '>', sam_fn],
                 'bsh'
               ))

    # Stage 5 SAM to BAM
    logger.info ('Preparing SAM to BAM conversion')
    bam_fn = bn + '.bam'
    cmds.append(([loc['samtools'], 'view', '-Sb', '-o', bam_fn, sam_fn], 'b'))

    # Stage 6 Sort
    logger.info ('Preparing BAM sorting')
    sorted_fn = bn + '_sorted.bam'
    cmds.append(([loc['samtools'], 'sort', '-f', '-@', threads, '-m', '2G', bam_fn, sorted_fn], 'b'))

    # Stage 7 optional deduplication
    if itrfce['Shared']['dedup']:
        logger.info ('Preparing BAM deduplication')
        dedup_fn = bn + '_dedup.bam'
        cmds.append(([loc['samtools'], 'rmdup', '-s', sorted_fn, dedup_fn], 'b'))
        finsrc = dedup_fn
    else:
        finsrc = sorted_fn

    # Stage 8 Link final
    logger.info ('Preparing final BAM file')
    final_fn = bn + '_final.bam'
    cmds.append(([ 'ln', finsrc, final_fn ], 'b'))

    # Stage 9 Index
    logger.info ('Preparing final indexing')
    cmds.append(([loc['samtools'], 'index', final_fn], 'b'))

    if tovcfprog=='mpileup':

        # Stage 10 mpileup
        logger.info ('Preparing Mpileup')
        bcf_fn = bn + '.bcf'
        cmds.append(([loc['samtools'], 'mpileup', '-uf', ref, final_fn, '>', bcf_fn], 'bsh'))

        # Stage 11 convert to VCF
        logger.info ('Preparing conversion to VCF')
        vcf_fn = bn + '.vcf'
        cmds.append(([loc['bcftools'], 'view', '-cvg', bcf_fn, '>', vcf_fn], 'bsh'))
    else:	# assert tovcfprog=='freebayes'

        # Stage 10 Freebayes
        logger.info ('Running freebayes')
        vcf_fn = bn + '.vcf'
        # cmd10 = [ freebayes, '-f', ref, final_fn, '|', 'vcffilter', '-f', '"QUAL > 20"', '>', vcf_fn ]
        cmds.append(([loc["freebayes"], '-f', ref, final_fn, '>', vcf_fn ], 'bsh'))

    # Stage 12 Restrict by snp panels
    logger.info('Preparing to filter loci')
    ai_fn = bn + '_ai.vcf'
    ii_fn = bn + '_ii.vcf'
    cmds.append(([loc['snp_convert.sh'], vcf_fn, ai_fn, ii_fn], 'b'))

    #vcf_filt_pfx = vcf_fn.split('.')[0] + '_filt'
    #cmd12 = ['vcftools', '--vcf', vcf_fn, '--out', vcf_filt_pfx, '--minDP', '50', '--recode', '--record-INFO-all']

    # Stage ? Restrict by Y-chrom and CODIS loci
    #logger.info('Preparing to filter loci')
    #ystr_fn = vcf_fn.split('.')[0] + '.ystr.txt'
    #codis_fn = vcf_fn.split('.')[0] + '.codis.txt'
    #cmd12 = ['/home/ngsforensics/forensicsapp/lobstr_convert.sh', vcf_fn, ystr_fn, codis_fn]

    # Upload results to DB
    #cmd13 = ['cd', com.default_directory, '&&',
    #         '/home/ngsforensics/forensicsapp/ngs_forensics/data/str2json.pl',
    #         '*lobstr*/*.txt', '>', 'all.json', '&&', 'mongoimport', '-h',
    #         'localhost:3001', '--db', 'meteor', '--collection', 'str', '--type',
    #         'json', '--drop', '--file', 'all.json', '--jsonArray']

    logger.info('Launching ToVCF pipeline using '+tovcfprog)
    success = px.run_pipeline(cmds, logger=logger, progress=progress)

    return success

if __name__ == '__main__':
    """ Run a Mpileup or Freebayes SNP calling pipeline """
    import sys
    import dummypb
    # define dummy interface output so we can get started
    interface = {
        'Shared': {
            'threads': '3',
            'r1': '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz',
            'R': '',	# has a default reference
            'single': True,
            'dedup': False,
            'tovcf': 'mpileup'	# or 'freebayes'
            # 'tovcf': 'freebayes'
        },
        'Trimmomatic': {
            'clip': 'ILLUMINACLIP:TruSeq3-SE:2:30:10',
            'sliding': 'SLIDINGWINDOW:4:15',
            'w': '4',
            'q': '15',
            'minlen': 'MINLEN:30',
            'm': '30',
            'phred': '-phred33',
        },
        'BWA': {
            'p': 'ILLUMINA', 'T': '30'
        },
        'mpileup': {},
    }

    # parameters for paired end testing
    if 0:	# set paired end values
        interface['Shared']['r1'] = '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz'
        interface['Shared']['single'] = 'single-end'

    if 0:	# run deduplication step
        interface['Shared']['dedup'] = True

    if 1:
        interface['Shared']['single'] = 'auto-detect'

    if len(sys.argv) == 2:
        interface['Shared']['r1'] = sys.argv[1]

    success = tovcf(interface, progress=dummypb.StatusProgress())
    if success:
        print 'ToVCF pipeline completed successfully'
    else:
        print 'ToVCF pipeline failed'
    print "... using", interface['Shared']['tovcf']
