#!/usr/bin/env python
"""
Support Module for Forensics Pipelines
Authors: Cameron Jack & Bob Buckley
ANU Bioinformatics Consultancy, John Curtin School of Medical Research,
Australian National University
18/5/2016
"""

import sys
import os
import subprocess
from timeit import default_timer as timer
import time
import logging

"""
    Library code for launching tasks to the shell.
    Allows for both blocking and non-blocking tasks.
"""

def get_logger(name, dn):
    """
    :input: name the name of the pipeline (hence the logging file)
    :input: project_dn the location of the output log file
    Moves the ugly code for setting logging outside the pipeline definition
    Should be in a utility module
    :return: logger object
    """
    # Set up pipeline logging
    log_path = os.path.join(dn, name+'.log')
    logger = logging.getLogger(name)
    assert logger
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s \t %(name)s \t %(levelname)s \t %(message)s')
    fh.setFormatter(formatter)
    formatter = logging.Formatter('%(name)s \t %(levelname)s \t %(message)s')
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def run_cmd(cmd_list, shell=False, logger=None):
    """ Launch a task, suitable to independent processes """
    cmds = map(str, cmd_list)
    if shell:
        cmds = ' '.join(cmds)
    try:
        # print "running:", cmds if shell else ' '.join(cmds)
        proc = subprocess.Popen(cmds, shell=shell, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        logger.info('Launched: ' + (cmds if shell else ' '.join(cmds)))
    except OSError:
        logger.error('Application not found')
        logger.error(' '.join(cmd_list))
        proc = None
    return proc

def dowait(job, inc, logger=None, progress=None):
    """ Wait for an async child process/job """
    stdout, stderr = job.communicate()
    logger.info("STDOUT:"+stdout)
    logger.info("STDERR:"+stderr)
    rc = job.wait()
    if rc!=0:
        logger.info("exit status: %d"%rc)
    progress.step(inc)
    return rc==0

def get_duration(start, stop):
    """
        Prints human readable duration between start and stop times
        using nice_time()
    """
    seconds = int(stop - start)
    minutes = seconds/60%60
    hours   = seconds/60/60
    msg = 'Time taken: %d hours, %d minutes, %d seconds' % (hours, minutes, seconds)
    return msg


def run_pipeline(run_order, logger=None, progress=None):
    """
        Choose appropriate actions for running or synching
        How to use: either 'sync' to wait for all non-blocking jobs
        OR a tuple of (job, mode), where job is a list of command segments
        and mode is one of b, bsh, nb, nbsh. b = blocking,
        nb = non-blocking, sh = requires shell (for redirection, piping)

        Accepts an optional progress/status bar object
    """
    started = timer()
    n = len(run_order)
    jobs = []
    for step, (cmd, mode) in enumerate(run_order, start=1):
        progress.status('Step', step, 'of', n)
        if cmd is None:
            progress.step(100/n)
            continue

        msg = ' '.join(map(str, [step, (cmd, mode)]))
        logger.debug(msg)

        # check for valid modes
        assert mode in [b+sh for b in ['b', 'nb'] for sh in ['', 'sh']]
        shell = mode.endswith('sh')	# use shell for command?
        nb = mode.startswith('nb')	# non-blocking
        id = run_cmd(cmd, shell=shell, logger=logger)
        if id:
            jobs.append((id, nb))
        else:
            msg = 'Pipeline failed at stage: '+str(step)
            logger.error(msg)
            break
        if not nb: 
            if not dowait(id, 100/n, logger=logger, progress=progress):
                break
        else:
            progress.step(50/n)

    # wait for all non-blocking jobs to finish ...
    jobcnt = len(jobs)
    for i, (job, nb) in enumerate(jobs, start=1):
        if nb:
            progress.status('finalise job no.', i, 'of', jobcnt)
            dowait(job, 50/n, logger=logger, progress=progress)

    progress.end()
    res = all(job.returncode==0 for job, nb in jobs)
    if not res:
        for i, (job, flag) in enumerate(jobs, start=1):
            if job.returncode!=0:
                msg = "Job no. %d. Return code = %d"%(i, job.returncode)
                logger.error(msg)
    logger.info(get_duration(started, timer()))

    return res

### END modpipe code ###
