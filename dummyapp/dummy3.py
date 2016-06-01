# -*- coding: utf-8 -*-

"""
This is the dummy3.py base module for testing fn.pyw
This module goes with several configuration files:
see cfg3.tab, cfg3.1.tab and cfg3.2.tab ... and the setup in appPages.py.
"""
import time
def pipecode(argdict, progress=None):
    print "dummy3.pipecode - argdict =", argdict
    # the following handles the progress bar in 5 steps = maximum=100
    if progress is not None:
        mx = progress.pb["maximum"]
        n = 3   # no. steps displayed on progress bar
        for i in range(n):
            progress.status("Step", i+1, "of", n)
            time.sleep(1)   # simulated work ... 
            progress.step(mx/n)
        progress.status("Done dummy3.")  # optional call to set 100% in progress bar
    return