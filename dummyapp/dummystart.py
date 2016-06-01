# -*- coding: utf-8 -*-
"""
Code that runs while the application's splash screen is being displayed.
It can update the progress bar and status.
This just xemonstrates what can be done. Normally it will do stuff like starting
background daemons and preparing the application environment.
"""

import subprocess
import time

sstime = 15 # no. seconds to display splash screen ... 

def main(progressbar=None):
    global sstime
    # the command needs to be run in the background if the splash screen progress bar
    # is going to move ...
    assert progressbar is not None
    sx, mx = 5, float(progressbar.pb["maximum"])-0.01
    for i in range(sx):
        progressbar.status("start step", i+1, "of", sx)
        subprocess.call("sh -c 'sleep 2'", shell=True)
        # time.sleep(2)
        progressbar.step(mx/sx)
    progressbar.status("Startup done")  
    return