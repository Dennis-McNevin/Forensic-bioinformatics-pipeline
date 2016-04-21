# -*- coding: utf-8 -*-
"""
Code that runs while the application's splash screen is being displayed.
It can update the progress bar and status.
This just xemonstrates what can be done. Normally it will do stuff like starting
background daemons and preparing the application environment.
"""

# import subprocess
import time

sstime = 20 # no. seconds to display splash screen ... 

def main(progressbar=None):
    # the command needs to be run in the background if the splash screen progress bar
    # is going to move ...
    assert progressbar is not None
    for i in range(10):
        progressbar.status("start step", i+1)
        # subprocess.call("sh -c 'sleep 10' &", shell=True)
        time.sleep(2)
        progressbar.step(10)
    progressbar.status("Done")  
    return