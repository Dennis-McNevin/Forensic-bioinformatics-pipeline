# -*- coding: utf-8 -*-

"""
This is a demo module for testing fn.pyw
and to show what can be done ... with the progress bar and status.
"""
import time
def run_pipeline(argdict, progress=None):
    print "run_pipeline - argdict =", argdict
    # the following handles the progress bar in 5 steps = maximum=100
    if progress is not None:
        mx = progress.pb["maximum"]
        n = 10   # no. steps displayed on progress bar
        for i in range(n):
            progress.status("Step", i+1, "of", n)
            time.sleep(2)   # simulated work ... 
            progress.step(mx/n)
        progress.status("All done.")
    return