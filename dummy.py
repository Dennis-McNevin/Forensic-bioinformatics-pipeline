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
        inc = mx/5
        for i in range(0, mx, inc): # total 100
            time.sleep(1)
            progress.step(inc)
    return