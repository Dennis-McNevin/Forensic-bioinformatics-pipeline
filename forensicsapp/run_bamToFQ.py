#!/usr/bin/env python

"""
BamToFASTQ pipeline

Authors: Cameron Jack & Bob Buckley
ANU Bioinformatics Consultancy,
John Curtin School of Medical Research,
Australian National University
18/5/2016

This code is part os the Forensics project.
"""

import os
import time
# import logging

import modpipe as px
import modcommon as com

files = [
          "gzip", 
        ]

def bamToFQ(itrfce, progress=None):
    """
        Pipeline for converting BAM contents to FASTQ

        Define a hardcoded pipeline that gets its optional command strings
        from Bob's interface code.

        itrface is a dictionary of dictionaries
    """
    assert 'Shared' in itrfce
    args = itrfce['Shared']
    srcdir = args['b']
    dstdir = args['d']
    if not dstdir:
       r = srcdir 
    date_and_time = time.strftime('%Y%m%d%H%M%S')
    logger = px.get_logger('bamToFQ'+date_and_time, dstdir)
    logger.info('Interface options: ' + str(itrfce))
    progress.status('Step 1 - extracting FASTQ file(s)')
    files, sf = com.bam2fq(srcdir, dstdir, args['single'])
    cmds = [(None, 'b')]	# first task shows up on progress bar
    for f in files:
        # use -f flag to avoid user dialog - force progress/overwrite
        cmds.append((['gzip', '-f', f], 'nb'))

    success = px.run_pipeline(cmds, logger=logger, progress=progress)
    if success:
        progress.status('conversion complete')

    return success

if __name__ == '__main__':
    """ run the BAM to FASTQ process"""
    import sys
    import dummypb as sp

    # define dummy interface output so we can get started
    interface = { 'Shared': {}, 'BAMtoFQ': {} }
    assert len(sys.argv) == 2

    interface['BAMtoFQ']['b'] = sys.argv[1]
    success = bamToFQ(interface, progress=sp.StatusProgress())

    if success:
        print 'BAM converted to FASTQ successfully'
    else:
        print 'BAM conversion to FASTQ failure'

