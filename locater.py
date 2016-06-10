# -*- coding: utf-8 -*-

"""
This code can scan a bunch of python files looking for 
uses of loc["xxx"] then it searches for a file called 'xxx'
in the file system and adds an entry to the locations dictionary.
The output is a file called 'location.py'

It is used to configure an applicatioin that calls various other programs.
"""

import sys
import re
import subprocess

if len(sys.argv)<2:
    sys.exit(0)

px = subprocess.PIPE
cmd = "find -L ~/mpsforensics/bin ~/bin /bin /usr/bin /usr/local/bin ~/mpsforensics /usr/local /var/share -name %s -type f 2>/dev/null"
jv = subprocess.check_output('ls /usr/share/java/trimmomatic-*.jar | sort | tail -n 1', shell=True).rstrip()
hdr = """

import os  
 
location = {
    'results': os.path.expanduser('~/mpsforensics/results'),
    #'gzip': '/bin/gzip',
    # this is not a real program - it's a directory and a program name
    'meteor': os.path.expanduser('~/mpsforensics/results/viewer/meteor'),
    'java-version': '%s',
""" % jv

files = {'results':'*** default ***', 'java-version' : jv, 'gzip': '/bin/gzip', }
with open('location.py', 'w') as dst:
    print >> dst, hdr.rstrip()
    for fn in sys.argv[1:]:
        with open(fn) as src:
            prog = src.read()
        for m in re.finditer(r'loc\s*\[\s*(["\'])([^"\']+)\1\s*\]', prog):
            target = m.group(2)
            if target in files:
                continue
            proc = subprocess.Popen(cmd%target, shell=True, stdout=px, stderr=px)
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
                print >> dst, "    '%s': '%s'," % (target, loc)
            else:
                loc = None
            files[target] = loc
    print >> dst, "  }"
    
missing = sorted(k for k, v in files.iteritems() if v is None)
if missing:
    print "Missing (not found) files:"
    for k in missing:
        print '   ', k
    print  
    import sys
    sys.exit(1)
