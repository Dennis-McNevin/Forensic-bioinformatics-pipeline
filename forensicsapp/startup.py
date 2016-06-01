# -*- coding: utf-8 -*-

import subprocess

sstime = 40 # no. seconds to display splash screen ... 

def main(pb):
    # the command needs to be run in the background if the splash screen progress bar
    # is going to move ...
    pb.status("Starting MPS Forensics application")
    pb.status("Starting meteor web service")
    subprocess.call("cd /home/ngsforensics/forensicsapp/ngs_forensics/ ; meteor &", shell=True)
    pb.step(100/3)
    pb.status("Starting IGV")
    subprocess.call("/home/ngsforensics/binaries/IGV_2.3.67/igv.sh", shell=True)
    pb.step(100/3)
    return
