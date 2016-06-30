#!/usr/bin/env python
"""
lobstr pipeline - single and paired end
Authors: Cameron Jack & Bob Buckley
ANU Bioinformatics Consultancy, John Curtin School of Medical Research,
Australian National University
18/5/2016
"""


import os
#import time
import modpipe as px
import modcommon as com
#import logging
#import sys
import location
loc = location.location

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

def lobstr(itrfce, progress=None):
    """
        Pipeline for running LobSTR STR caller in single- and paired-end mode

        Define a hardcoded pipeline that gets its optional command strings
        from Bob's interface code.

        itrfce is a dictionary of dictionaries, with each top level key
        being a pipeline stage and each second level key being the
        argument and the value being the value of said argument.

        progress is a progress bar and status line object for user feedback
    """
    global loc

    cmdsamtools = loc['samtools']

    trim_fq, bn, cmds, pipedir, logger = com.prepare(itrfce, 'lobstr', progress)
    # note: len(trim_fq)==1 for single end, ==2 for paired-end data
    assert bn.startswith(pipedir)

    threads = itrfce['Shared']['threads']

    # LobSTR specific
    LOBINDEX = '~/mpsforensics/lobstr_ref/hg19_v3.0.2/lobstr_v3.0.2_hg19_ref/lobSTR_'
    LOBINFO  = '~/mpsforensics/lobstr_ref/hg19_v3.0.2/lobstr_v3.0.2_hg19_strinfo.tab'
    LOBNOISE = '~/mpsforensics/lobstr_ref/share/lobSTR/models/illumina_v3.pcrfree'

    # stage 4 LobSTR.
    logger.info ('Preparing LobSTR alignment')
    bam_fn = bn + '.aligned.bam'
    # prefix_fn = trim_fq.split('.')[0]
    cmd4x = [x for xs in zip((['--p1', '--p2'] if len(trim_fq)==2 else ['-f']), trim_fq) for x in xs ] 
    cmd4 = [loc['lobSTR'],
            '--index-prefix', LOBINDEX,
            '-p', threads, '-q'
           ] + cmd4x + \
           [
            '--rg-sample', pipedir, '--rg-lib', pipedir, '--out', bn]
    logger.debug ('LobSTR options')
    logger.debug (itrfce['LobSTR'])
    logger.debug ('Allelotype options')
    logger.debug (itrfce['allelotype'])
    add_args(itrfce['LobSTR'], cmd4)

    if trim_fq[0].endswith('.gz'):
        cmd4.append('--gzip')
    cmds.append((cmd4, 'bsh'))

    # Stage 5 Sort
    logger.info ('Preparing BAM sorting')
    sorted_fn = bn + '_sorted.bam'
    cmd5 = [cmdsamtools, 'sort', '-f', '-@', threads, '-m', '2G', bam_fn, sorted_fn]
    cmds.append((cmd5, 'b'))

    # Stage 6 Index
    logger.info ('Preparing BAM indexing')
    cmd6 = [cmdsamtools, 'index', sorted_fn]
    cmds.append((cmd6, 'b'))

    # Stage 7 LobSTR
    logger.info ('Preparing LobSTR allelotyping')
    str_fn = bn + '_lobstr'

    cmd7 = [loc['allelotype'],
            '--index-prefix', LOBINDEX, '--strinfo', LOBINFO,
            '--command', 'classify', '--noise_model', LOBNOISE, 
            '--bam', sorted_fn,
            '--haploid', 'chrX,chrY', 
            '--out', str_fn]
    add_args(itrfce['allelotype'], cmd7)
    cmds.append((cmd7, 'bsh'))

    # Stage 8 Restrict by Y-chrom and CODIS loci
    logger.info ('Preparing to filter loci')
    vcf_fn = str_fn + '.vcf'
    ystr_fn = str_fn + '.ystr.txt'
    codis_fn = str_fn + '.codis.txt'
    cmd8 = [loc['lobstr_convert.sh'], vcf_fn, ystr_fn, codis_fn]
    cmds.append((cmd8, 'b'))

    # Stage 9 create Excel-friendly CSV file
    cmd9 = [loc['VCFtoExcel.py'], vcf_fn]
    cmds.append(cmd9, 'b')

    # Upload results to DB
    cmd10 = [loc['load_results.sh']]
    cmds.append((cmd10, 'b'))

    logger.info ('Launching pipeline')
    success = px.run_pipeline(cmds, logger=logger, progress=progress)

    return success

if __name__ == '__main__':
    """ Run the single-end LobSTR STR calling pipeline """

    # define dummy interface output so we can get started
    interface = {
        'Shared': {
            'threads': '2',
            'r1': '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz',
            'single': 'single-end',
        },
        'Trimmomatic': {
            'c': False,
            # 'clip': 'ILLUMINACLIP:TruSeq3-SE:2:30:10',
            's': True,
            'w': '4',
            'q': '15',
            # 'minlen': 'MINLEN:30',
            'd': False,
            'm': '30',
            # 'phred': '-phred33',
        },
        'LobSTR': {
            'min-bp-before-indel': '7',
            'maximal-end-match': '15',
            'min-read-end-match': '5',
            'min-border': '5'
        }
    }
    import sys
    import dummypb
    if 0:
        interface['Shared']['single'] = 'auto-detect'
    if len(sys.argv) == 2:
        interface['Shared']['r1'] = sys.argv[1]

    success = lobstr(interface, progress=dummypb.StatusProgress())
    if success:
        print 'LobSTR pipeline completed successfully'
    else:
        print 'LobSTR pipeline failed'


