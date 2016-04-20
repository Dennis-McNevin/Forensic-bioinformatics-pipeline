# -*- coding: utf-8 -*-

"""
This is a stub module for testing fn.pyw
"""
import time
def run_pipeline(argdict, progress=None):
    print "run_pipeline - argdict =", argdict
    # the following handles the progress bar in 5 steps = maximum=100
    if progress is not None:
        mx = progress.pb["maximum"]
        n = 5   # no. steps displayed on progress bar
        for i in range(n):
            progress.status("Step", i+1, "of", n)
            time.sleep(1)   # simulated work ... 
            progress.step(mx/n)
        progress.end()  # optional call to set 100% in progress bar
    return