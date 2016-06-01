#!/usr/bin/env python

import os
import time
import modpipe as px
import modcommon as com

strrazor_home = '/home/bobb/Downloads/STRaitRazorv2.5/Newest_STRait_Razor'
destdir = '/home/ngsforensics/results'

def strrazor(itrfce, progress=None):
    """
        Pipeline for running STRaitRazor script

        Define a hardcoded pipeline that gets its optional command strings
        from Bob's interface code.

        itrfce is a dictionary of dictionaries, with each top level key
        being a pipeline stage and each second level key being the
        argument and the value being the value of said argument.

        progress is an optional progress bar object we can update
    """
    global strrazor_home, destdir

    for sect in ['Shared', 'Trimmomatic', 'strrazor']: 
        if not sect in itrfce:
            print sect, "is not present in the interface dictionary :("
            return False

    fqs, bn, cmds, logger = com.prepare(itrfce, 'STRaitRazor', progress)

    # target directory must not be present
    wkdir = os.path.join(destdir, itrfce['strrazor']['sample'])
    cmd = [ 'test', '-d', wkdir, '&&', 'rm', '-rf', wkdir, ';', 'true' ]
    cmds.append((cmd, 'bsh'))

    # run STRaitRazor
    cmd = [ 'cd', strrazor_home, ';', 'perl', './STRaitRazor.pl', '-dir',
             destdir ] + [ x for f in fqs for x in [ '-fastq', f ]] + [
             '-sampleNum', itrfce['strrazor']['sample'],
             '-typeselection', itrfce['strrazor']['opt'],
          ]
    cmds.append((cmd, 'bsh'))

    success = px.run_pipeline(cmds, logger=logger, progress=progress)

    return success

if __name__ == '__main__':
    """ Run a Mpileup or Freebayes SNP calling pipeline """
    import sys
    import dummypb
    # define dummy interface output so we can get started
    interface = {
        'Shared': {
            'r1': '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz',
            'single': 'single-end',
            'threads': '3',
        },
        'Trimmomatic': {'a': '', 'c': 0, 'd': 0, 'm': '20', 'q': '20', 's': 1, 'w': '4'}, 
        'strrazor': {
            'sample': 'S5',
            'opt' : 'ALL',	# choice of X, Y, AUTOSOMAL, ALL
        },
    }

    # parameters for paired end testing
    if 0:	# set paired end values
        interface['Shared']['r1'] = '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz'


    if 1:
        interface['Shared']['single'] = 'auto-detect'

    if len(sys.argv) == 2:
        interface['Shared']['r1'] = sys.argv[1]

    success = strrazor(interface, progress=dummypb.StatusProgress())
    if success:
        print 'STRaitRazor pipeline completed successfully'
    else:
        print 'STRaitRazor pipeline failed'
