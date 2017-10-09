#!/usr/bin/env python

"""
Mpileup and Freebayes pipeline

Authors: Cameron Jack & Bob Buckley
ANU Bioinformatics Consultancy,
John Curtin School of Medical Research,
Australian National University
18/5/2016

This code is part of the Forensics project.
It uses mpileup or freebayes to get a SNP VCF file ...
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

def add_args(arg_dict, cmd):
    """
        Go through args dict and add arguments to command line
    """
    for key in arg_dict.keys():
        if isinstance(arg_dict[key], str):
            if len(key) == 1:
                cmd.append('-' + key)
                cmd.append(arg_dict[key])
            else:
                cmd.append('--' + key)
                cmd.append(arg_dict[key])
        elif arg_dict[key] != 0: # include if true
            if len(key) == 1:
                cmd.append('-' + key)
                #cmd.append(arg_dict[key])
            else:
                cmd.append('--' + key)
                #cmd.append(arg_dict[key])


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
    if 'R' not in itrfce['Shared']:
        itrfce['Shared']['R'] = loc['human.fa']
    ref = itrfce['Shared']['R']

    # Stage 4 BWA
    logger.info ('Preparing BWA alignment')
    sam_fn = bn + '.sam'
    cmd4 = [loc['bwa'], 'mem', '-t', threads]
    add_args(itrfce['BWA'], cmd4)
    cmd4.append(ref)
    cmd4 += trim_fq # trim_fq is a list so it adds
    cmd4.append('>')
    cmd4.append(sam_fn)
    cmds.append((cmd4, 'bsh'))

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
        cmd10 = [loc['samtools'], 'mpileup']
        add_args(itrfce['mpileup'],cmd10)
        cmd10 += ['-uf', ref, final_fn, '>', bcf_fn]
        cmds.append((cmd10, 'bsh'))
        #cmds.append(([loc['samtools'], 'mpileup', '-uf', ref, final_fn, '>', bcf_fn], 'bsh'))

        # Stage 11 convert to VCF and filter by known loci then correct missing genotypes
        logger.info ('Preparing conversion to VCF')
        vcf_loci_fn = bn + '_loci.vcf'
        cmds.append(([loc['bcftools'], 'view', '-cgl', loc['snp_loci.txt'], bcf_fn, '>', vcf_loci_fn], 'bsh'))
        vcf_fn = bn + '.vcf'
        cmds.append((['python', loc['fix_genotypes.py'], vcf_loci_fn, '>', vcf_fn], 'bsh'))
    else:	# assert tovcfprog=='freebayes'

        # Stage 10 Freebayes
        logger.info ('Running freebayes')
        vcf_fn = bn + '.vcf'
        # cmd10 = [ freebayes, '-f', ref, final_fn, '|', 'vcffilter', '-f', '"QUAL > 20"', '>', vcf_fn ]
        cmd10 = [loc['freebayes']]
        add_args(itrfce['freebayes'], cmd10)
        cmd10 += ['-f', ref, final_fn, '>', vcf_fn]
        cmds.append((cmd10, 'bsh'))
        #cmds.append(([loc["freebayes"], '-f', ref, final_fn, '>', vcf_fn ], 'bsh'))

    # Stage 12 Restrict by snp panels
    logger.info('Preparing to filter loci')
    snp_fn = bn + '.snp.txt'
    cmds.append(([loc["bedtools"], 'intersect', '-b', vcf_fn, '-a', loc["standard.pnl"], #$HOME/mpsforensics/standard.pnl,
            '-wb', '>', snp_fn], 'bsh'))

    # Stage 13 upload to DB
    logger.info('Uploading to DB')
    cmds.append(([loc['load_results.sh']], 'b'))

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
