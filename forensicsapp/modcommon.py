#!/usr/bin/env python
"""
common pipeline startup
Authors: Cameron Jack & Bob Buckley
ANU Bioinformatics Consultancy, John Curtin School of Medical Research,
Australian National University
18/5/2016

Extract FASTQ from a BAM file if that's the starting point
Run FASTQC and Trimmomatic ...
"""

import os
import sys
import time
import re
import subprocess
import glob
import tkMessageBox as tkmb

import modpipe as px

files = [
          'java', 'picard.jar', 
          'fastqc', 
          'TrimmomaticSE', 'TrimmomaticPE',
          # 'fastqc' again
        ]

# set up default directories/locations
forensicsvar = [('FORENSICSHOME', ":".join(filter(os.path.isdir, map(os.path.expanduser, '~/forensics:/usr/local:/home/ngsforensics'.split(':'))))), 
                ('FORENSICSRESULTS', os.path.expanduser('~/mpsforensics/results'))
               ]
forensicsenv = tuple(os.getenv(x,d) for x,d in forensicsvar)

def initcheck():
    global forensicsvar, forensicsenv
    if not all(forensicsenv):
        tkmb.showerror("Environment variables", 
            "This program needs several enviroment variables set.\n"
            "Currently not set:\n  " +
            "\n  ".join(k for k, v in zip(forensicsvar, forensicsenv) if not v))
        sys.exit(1)
    if not forensicsenv[1]:
        tkmb.showerror("Unknown results directory", """
Unknown results directory: 
please set the FORENSICSRESULTS environment variable
before you run this program.
""")
        sys.exit(1)
    return

def getexec(cmdname, pd=[]):
    """
    Try to find the required executable for cmdname ...
    pd is a list of directories for the specific program (this was useful
        when we were developing since the executables were in their own
        specific directories)
    """
    global forensicsenv
    home = forensicsenv[0]
    progs = (os.path.join(os.path.expanduser(d), 'bin', cmdname) for d in home.split(':')+pd)
    return (p for p in progs if os.path.isfile(p)).next()

def bam2fq(srcnm, dstdir, sf):
    """
	Input is a BAM file ... extract FASTQ file(s)
    """
    jarfile = '/home/ngsforensics/forensicsapp/binaries/picard-tools-2.2.1/picard.jar'
    srcdir, srcname = os.path.split(srcnm)
    bn, ext = os.path.splitext(srcname)
    assert ext in ['.bam', '.ubam']
    fn, fn1, fn2 = [os.path.join(dstdir, bn+x+'.fq') for x in ['', '_1', '_2']]
    if sf.startswith('single'):
        cmd = ['java', '-jar', jarfile, 'SamToFastq', 'I='+srcnm, 'F='+fn]
        res = subprocess.call(cmd, shell=False)
        assert res==0	# needs better testing
        return [fn], sf

    cmd = ['java', '-jar', jarfile, 'SamToFastq', 'I='+srcnm, 'F='+fn1, 'F2='+fn2]
    res = subprocess.call(cmd, shell=False)
    assert res==0	# needs better result check!
    if os.path.isfile(fn2):
        ss = os.stat(fn2)	# use os.stat() to get file size
        if ss.st_size==0:
            assert not sf.startswith('pair')	# needs to complain to user via GUI
            os.remove(fn2)
            sf = 'single-end'
        elif sf.startswith('auto'):
            sf = 'paired-end'
     
    else:	#doubt that it gets here ... more likely we got an empty file
        sf = 'single-end'
    if sf.startswith('single'):
        os.rename(fn1, fn)
        return [fn], sf
    return [fn1, fn2], 'paired-end'

def prepare(itrfce, pipename, progress=None, trim=True):
    """
        Pipeline for running LobSTR STR caller in single- and paired-end mode

        Define a hardcoded pipeline that gets its optional command strings
        from Bob's interface code.

        itrfce is a dictionary of dictionaries, with each top level key
        being a pipeline stage and each second level key being the
        argument and the value being the value of said argument.

        progress is a progress bar and status line object for user feedback

        Note: fastqc and java commands are expected to be in the PATH variable
    """
    args = itrfce['Shared']
    cmds = []
    global forensicsenv
    home, default_directory = forensicsenv
    results = args['results'] if 'results' in args else default_directory 
    # couple of useful properties to have for the pipeline
    sflag = args['single']
    assert any(sflag.startswith(x) for x in ['auto', 'single', 'paired'])
    r1 = args['r1']

    # build a directory to put all pipeline results in
    date_and_time = time.strftime('%Y%m%d%H%M%S')
    srcdir, tmp = os.path.split(r1)
    tmp = '_'.join([tmp.split('.',1)[0], pipename, date_and_time])
    proj_dn = os.path.join(results, tmp)
    if not os.path.isdir(proj_dn):
        os.makedirs(proj_dn)

    if any(r1.endswith(x) for x in ['.bam', '.ubam']):
        # this is a BAM (or unmapped BAM) file ... we need to extract the FASTQ file(s)
        # and discover if it's SE or PE data
        files, sflag = bam2fq(r1, proj_dn, sflag)
        cmds.append((None, 'b'))	# progress is shown for first step
        for fn in files:
            cmds.append((['gzip', '-f', fn], 'nb')), 
        files = [fn+'.gz' for fn in files]
        r1 =files[0]
    elif any(sflag.startswith(x) for x in ['auto', 'paired']):
        # find a paired-end file if it exists ??? use glob.glob
        srcdir, fn = os.path.split(r1)
        fnpat = re.sub('(_R?)1($|(?=[._L]))', '\g<1>[12]', fn)
        # print "looking for files:", fnpat
        files = sorted(glob.glob(os.path.join(srcdir, fnpat)))
        # print "glob gives:", files
        assert files[0]==r1
        assert len(files)<=2
        if sflag.startswith('paired'):
            assert len(files)==2
        elif len(files)==2:
            sflag = 'paired-end'
        elif len(files)==1:
            sflag = 'single-end'
    else:	# single-end
        files = [r1]

    # print "files =", files

    dirhdr, fname = os.path.split(r1)
    fn1, ext = fname.split('.',1)	# split at first dot!
    gz = '.gz' if fname.endswith('.gz') else ''

    ending = 'SE' if sflag.startswith('single') else 'PE'

    bn = os.path.join(proj_dn, fn1)
    bn1 = bn
    if ending=='PE':
        r2 = files[1]
        fn2, tmp = os.path.split(r2)[1].split('.', 1)
        
        # find a paired file ... ???
        # basename without pairing end identifier
        bn = re.sub('_R?1($|(?=[._L]))', '', fn1, count=1)
        bn = os.path.join(proj_dn, bn)
        bn2 = os.path.join(proj_dn, fn2)
        # print "r1              =", r1
        # print "looking for file:", r2
        # assert os.path.isfile(r2)

    logger = px.get_logger(pipename+ending, proj_dn)

    logger.info('Interface options: ' + str(itrfce))
    if gz:
        logger.info('Using zipped data.')

    threads = args['threads']

    # Stage 1 FASTQC
    logger.info ('Preparing FASTQC on raw data')
    cmd1 = ['fastqc', '-f', 'fastq', '-q', '-O', proj_dn, r1]
    if ending=='PE':
        cmd1.append(r2)

    # Stage 2 Trimmomatic
    # trimlog = os.path.join(proj_dn, 'raw_trimlog.txt')
    if ending=='SE':
        trim_in = [ r1 ]
        trim_fq = [ bn+'_trimmed.fq'+gz ]
        trim_x  = trim_fq
    else:
        trim_in = [ r1, r2 ]
        trim_fq = [ n+'_trimmed.fq'+gz for n in [bn1, bn2] ]
        trim_x  = [ n + x + '.fq'+gz for n in [bn1, bn2] for x in ['_trimmed', '_unpaired'] ]

    logger.info ('Preparing Trimmomatic')
    cmd2 = ['Trimmomatic'+ending, '-threads', threads, '-phred33'] + trim_in + trim_x + ['AVGQUAL:'+itrfce['Trimmomatic']['q']] 

    # if 'clip' in itrfce:
    #    cmd2.append(itrfce['clip']) # need to have an adapter file

    if itrfce['Trimmomatic']['s'] and all(c in itrfce['Trimmomatic'] for c in "qw"):
        sliding = ':'.join(['SLIDINGWINDOW', itrfce['Trimmomatic']['w'], itrfce['Trimmomatic']['q']])
        cmd2.append(sliding)
    if itrfce['Trimmomatic']['d'] and 'm' in itrfce['Trimmomatic']:
        minlen = ':'.join(['MINLEN', itrfce['Trimmomatic']['m']])
        cmd2.append(minlen)

    # Stage 3 FASTQC
    logger.info ('Preparing FASTQC on trimmed data')
    cmd3 = ['fastqc', '-f', 'fastq', '-q', '-O', proj_dn] + trim_fq

    # the common commands for used for several pipelines
    cmds += [(cmd1, 'nb'), (cmd2, 'b'), (cmd3, 'nb')]

    return trim_fq, bn, cmds, proj_dn, logger

if __name__ == '__main__':
    """ Run the 'common' pipeline """

    # define dummy interface output so we can get started
    interface = {
        'Shared': {
            'r1': '/home/cam/projects/forensics/forensics_data/MiSeq_DFSC/R701-A506_S5_L001_R1_001.fastq.gz',
            'single': 'single-end',
            'threads': '2'
        },
        'Trimmomatic': {
            'clip': 'ILLUMINACLIP:TruSeq3-SE:2:30:10',
            'sliding': 'SLIDINGWINDOW:4:15',
            'w': '4',
            'q': '15',
            'minlen': 'MINLEN:30',
            'm': '30',
            'phred': '-phred33',
        }
    }
    if 0:
        interface['Shared']['single'] = 'paired-end'
    if 1:
        interface['Shared']['single'] = 'auto-detect'

    import dummypb
    if len(sys.argv) == 2:
        interface['Shared']['r1'] = sys.argv[1]

    res = prepare(interface, 'common', progress=dummypb.StatusProgress())

    print "prepare(...) returns:"
    print "   trim_fq =", res[0]
    print "   bn =", res[1]
    for cmd in res[2]:
        print "\t", cmd

