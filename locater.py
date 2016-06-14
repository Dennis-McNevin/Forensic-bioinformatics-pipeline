# -*- coding: utf-8 -*-

"""
This code can scan a bunch of python files looking for 
uses of loc["xxx"] then it searches for a file called 'xxx'
in the file system and adds an entry to the locations dictionary.
The output is a file called 'location.py'

It is used to configure an applicatioin that calls various other programs.
"""

import sys
import os
import re
import subprocess

if len(sys.argv)<2:
    sys.exit(0)

# the following are expected to be present ... or installed with apt-get
native = [
    'gcc',
    'g++',
    'java',
    'gfortran',
    'bwa',
    'samtools', 'bcftools', 'vcftools', 'bedtools',
    'curl',
    'mongodb', 'mongoimport',
    'firefox',
    'git',
    'gzip', 'gunzip',
    'perl', 'python',
]

cmd = "find -L ~/mpsforensics/viewer ~/mpsforensics/bin ~/mpsforensics/help ~/mpsforensics /var/share ~ -name %s -type f 2>/dev/null"
npath = [x for x in os.getenv('PATH').split(':') if not x.endswith('games')]
ncmd ="find -L "+' '.join(npath)+" -name %s -type f 2>/dev/null"

location = {
    'results': "os.path.expanduser('~/mpsforensics/results')",
    # 'meteor' is not a real program - it's a directory and a program name
    'meteor': "os.path.expanduser('~/mpsforensics/results/viewer/meteor')",
  }

jv = subprocess.check_output('ls /usr/share/java/trimmomatic-*.jar | sort | tail -n 1', shell=True).rstrip()
if not jv:
    sys.exit(1)
    
location['java-version'] = "'"+jv+"'"
px = subprocess.PIPE
      
for fn in sys.argv[1:]:
    with open(fn) as src:
        prog = src.read()
    for m in re.finditer(r'loc\s*\[\s*(["\'])([^"\']+)\1\s*\]', prog):
        target = m.group(2)
        if target in location:
            continue
        xcmd = ncmd if target in native else cmd
        proc = subprocess.Popen(xcmd%target, shell=True, stdout=px, stderr=px)
        proc.wait()
        out, err = proc.communicate()
        out = out.rstrip()
        if out:
            locs = out.split('\n')
            # remove duplicates
            for i in range(len(locs)-1, 0, -1):
                if locs[i] in locs[0:i]:
                    del locs[i]
            loc = locs[0]
            if len(locs)>1:
                print "\nCandidates for", target
                print loc, '** chosen'
                print '\n'.join(locs[1:])
            loc = "'"+loc+"'"
        else:
            loc = None
        location[target] = loc
        
hdr = """

import os  

location = {
""" 
with open('location.py', 'w') as dst:
    print >> dst, hdr.rstrip()
    for k, v in location.iteritems():
        if v:
            print >> dst, "    '"+k+"'", ':', v+","
    print >> dst, "  }"
    
missing = sorted(k for k, v in location.iteritems() if v is None)
if missing:
    print "Missing (not found) files:"
    for k in missing:
        print '   ', k
    print  
    sys.exit(1)
