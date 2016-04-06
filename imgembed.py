# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 22:42:46 2014

@author: Bob Buckley

This program reads a Python tkinter program and embeds images
used in the program. This means the program with its image is a single
file. It can be copied to various locations and it will still work even
if the image file is not copied.

You have to put the commenst of the right form and read the data just the
right way for this to work ... see comments below.

We suggest the image data is embedded near the end of the program so the
program remains relatively readable.
"""
import base64
import re
import sys

def addgif(fn):
    "read a file and convert it to a multi-line base64 encoded string ..."
    with open(fn, 'rb') as src:
        data = base64.b64encode(src.read())
    n = 72
    lines = (data[i:i+n] for i in range(0, len(data), n))
    return '"""\n'+'\n'.join(lines)+'"""\n'

def dofile(fnsrc, fndst=None):
    """process the lines of a file; looking for ##embed comments ...
    then do the required substitutions"""
    imgs = 0
    with open(fnsrc) as src, open(fndst, 'w') if fndst else sys.stdout as dst:
        for lx in src:
            if not re.match(r'\s*##\s*embed', lx):
                dst.write(lx)
                continue
            # read the next 3 lines. They should be ...
            # import base64
            # with open(fn) as src:
            #     var = base64.b64encode(src.read())
            # we need to convert this to ...
            # var = """ ... """
            lxs = src.next(), src.next(), src.next()
            pat = r'(\s*)with open\(["\']([^"\']*)["\'].*\).*:' \
                    r'\s+(\S+\s*=\s*)base64.b64encode'
            mfn = re.match(pat, lxs[1].rstrip()+lxs[2])
            if not mfn:
                print "bad embed code ..."
                print ''.join(lxs)
                sys.exit(1)
            efn = mfn.group(2)
            if not efn.lower().endswith('gif'):
                print "Only embed GIF files ... not", efn
                sys.exit(1)
            dst.write(mfn.group(1)+mfn.group(3) + addgif(efn))
            imgs += 1
    print >> sys.stdout if fndst else sys.stderr, "embedded", imgs, "images"
    return

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print "usage: python imgembed.py infile [outfile]"
        sys.exit(1)
    dofile(*sys.argv[1:])
