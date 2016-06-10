# -*- coding: utf-8 -*-

import subprocess
import os
import time
# import modcommon as com
# import tkMessageBox as tkmb
import location

sstime = 40 # no. seconds to display splash screen ... 

def main(pb, Splash=None):
    # the command needs to be run in the background if the splash screen progress bar
    # is going to move ...
    # tkmb.showinfo("Say hello", "Hello!")
    loc = location.location
    os.umask(0077)	# make all files that are created private
    pb.status("Starting MPS Forensics application")
    pb.status("Starting meteor web service")
    mdir, mprog = os.path.split(loc['meteor'])
    cmd = ["cd", mdir, ';', mprog, '&', ]
    time.sleep(3)
    subprocess.Popen(cmd, shell=True)
    pb.step(6)
    pb.status("Starting IGV")
    subprocess.Popen([loc["igv.sh"], '&', ], shell=True)
    time.sleep(3)
    pb.step(6)
    for i in range(40-6):
        if Splash:
            Splash.front()
        time.sleep(1)
        pb.step(2)
    return
