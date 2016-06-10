# -*- coding: utf-8 -*-

import subprocess
import os
# import modcommon as com
# import tkMessageBox as tkmb
import location

sstime = 40 # no. seconds to display splash screen ... 

def main(pb):
    # the command needs to be run in the background if the splash screen progress bar
    # is going to move ...
    # tkmb.showinfo("Say hello", "Hello!")
    loc = location.location
    os.umask(0077)	# make all files that are created private
    pb.status("Starting MPS Forensics application")
    pb.status("Starting meteor web service")
    mdir, mprog = loc['meteor']
    cmd = ["cd", mdir, ';', mprog, '&' ]
    subprocess.call(cmd, shell=True)
    pb.step(100/3)
    pb.status("Starting IGV")
    subprocess.call(loc["igv.sh"], shell=True)
    pb.step(100/3)
    return
