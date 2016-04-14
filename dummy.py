# -*- coding: utf-8 -*-

"""
This is a stub module for testing fp.pyw
"""
import time
def run_pipeline(argdict, progress=None):
    print "run_pipeline - argdict =", argdict
    # the following handles the progress bar in 5 steps = maximum=100
    if progress is not None:
        mx = progress["maximum"]
        n = 5
        for i in range(n): # total 100
            progress.status("Step", i+1, "of", n)
            time.sleep(1)
            progress.step(mx/n)
    return