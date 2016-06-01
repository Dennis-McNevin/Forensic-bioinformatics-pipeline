#!/usr/bin/env python

import os
import time
import modpipe as px
import modcommon as com

def mpileup(itrfce, progress=None):
    """
        Pipeline for running mpileup in single-end mode

        Define a hardcoded pipeline that gets its optional command strings
        from Bob's interface code.

        itrface is a dictionary of dictionaries, with each top level key
        being a pipeline stage and each second level key being the
        argument and the value being the value of said argument.

        progress is an optional progress bar object we can update
    """

    trim_fq, bn, cmds, logger = com.prepare(itrfce, 'mpileup', progress)

    # Stage 4 BWA
    logger.info ('Preparing BWA alignment')
    sam_fn = bn + '.sam'
    cmd4 = ['bwa', 'mem', '-t', itrfce['Shared']['threads'],
            itrfce['Shared']['R']] + trim_fq + [ '>', sam_fn]

    # Stage 5 SAM to BAM
    logger.info ('Preparing SAM to BAM conversion')
    bam_fn = bn + '.bam'
    cmd5 = ['samtools', 'view', '-Sb', '-o', bam_fn, sam_fn]

    # Stage 6 Sort
    logger.info ('Preparing BAM sorting')
    sorted_fn = bam_fn.split('.')[0] + '_sorted.bam'
    cmd6 = ['samtools', 'sort', '-f', '-@', itrfce['Shared']['threads'],
            '-m', '2G', bam_fn, sorted_fn]

    # Stage 7 Index
    logger.info ('Preparing BAM indexing')
    #indexed_fn = sorted_fn.split('.')[0] + '_indexed.bam'
    cmd7 = ['samtools', 'index', sorted_fn]

    # Stage 8 rmdup
    #logger.info ('Preparing BAM deduplication')
    #dedup_fn = sorted_fn.split('.')[0] + '_dedup.bam'
    #cmd8 = ['samtools', 'rmdup', '-s', sorted_fn, dedup_fn]
    cmd8 = None

    # Stage 9 Index
    #logger.info ('Preparing final indexing')
    #cmd9 = ['samtools', 'index', dedup_fn]
    cmd9 = None

    # Stage 10 mpileup
    logger.info ('Preparing Mpileup')
    #bcf_fn = dedup_fn.split('.')[0] + '.bcf'
    bcf_fn = sorted_fn.split('.')[0] + '.bcf'
    cmd10 = ['samtools', 'mpileup', '-uf', itrfce['Shared']['R'],
             sorted_fn, '>', bcf_fn]

    # Stage 11 convert to VCF
    logger.info ('Preparing conversion to VCF')
    vcf_fn = bcf_fn.split('.')[0] + '.vcf'
    cmd11 = ['bcftools', 'view', '-cvg', bcf_fn, '>', vcf_fn]

    # Stage 12 Restrict by snp panels
    logger.info('Preparing to filter loci')
    ai_fn = vcf_fn.split('.')[0] + '_ai.vcf'
    ii_fn = vcf_fn.split('.')[0] + '_ii.vcf'
    cmd12 = ['/home/ngsforensics/forensicsapp/snp_convert.sh', vcf_fn, ai_fn, ii_fn]

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

    cmds += [(cmd4, 'bsh'),
                 (cmd5, 'b'), (cmd6, 'b'), (cmd7, 'b'), (cmd8, 'b'), (cmd9, 'b'),
                 (cmd10, 'bsh'), (cmd11, 'bsh'), (cmd12, 'b')]

    logger.info('Launching Mpileup pipeline')
    success = px.run_pipeline(cmds, logger=logger, progress=progress)

    return success

if __name__ == '__main__':
    """ Run a Mpileup (or freebayes) SNP calling pipeline """
    import sys
    import dummypb
    # define dummy interface output so we can get started
    interface = {
        'Shared': {
            'threads': '2',
            'r1': '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz',
            'R': '/home/ngsforensics/human/human.fa',
            'single': True
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
        # 'LobSTR': {}
    }

    # parameters for paired end testing
    if 0:
        interface['Shared']['r1'] = '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz'
        # interface['Shared']['r2'] = '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R2_001.fastq.gz',
        interface['Shared']['single'] = False

    if len(sys.argv) == 2:
        interface['Shared']['r1'] = sys.argv[1]

    success = mpileup(interface, progress=dummypb.StatusProgress())
    if success:
        print 'Mpileup pipeline completed successfully'
    else:
        print 'Mpileup pipeline failed'
