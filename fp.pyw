#!/usr/bin/env python
"""
    NGS Forensic GUI and Pipeline Caller
    author: Bob Buckley, ANU Bioinformatics Consultancy, 
        John Curtin School of Medical Research, Australian National University
    4-APR-2016
    
    This program reads a configuration file cfg.tab (tab separated descriptors)
    and builds a dictionary that conatins run arguments.
    
    When the 'run' button is pressed, it calls an external procedure run_pipeline(argdict)
    that hopefully does the work.
    
    To do:
        - maybe add a menu bar
        - maybe, display progress ... in a progress bar? 
    
"""

from __future__ import print_function

__version__ = "0.1-a2"
__progname__ = "NGS Forensics Pipeline"

status = print

# import os
# import re
# import array
import sys
# import string


# import argparse
    
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import ttk
import collections

import dummy as code # This is where the work is specified ... just import the right module
                     # with a run_pipe procedure that has the argument dictionary as its parameter

class ifrow:
    """
    Superclass for an Interface row.
    
    Every row has a label ... so handle it here.
    """
    def __init__(self, master, cfgline):
        self.flg = cfgline.flag
        self.var = None
        self.default = cfgline.default
        w0 = ttk.Label(master, text=cfgline.label)
        w0.grid(row=master.rows, column=0, sticky='e')
        master.vars.append(self)
        return
    
    def myflags(self):
        return self.flg, self.var.get()
    
class ivar(ifrow):
    """Integer input in interface"""
    def __init__(self, master, cfgline):
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.flg = cfgline.flag
        self.default = cfgline.default
        self.var = tk.StringVar()
        self.var.set(self.default)
        f,t = cfgline.constraint.split('-',1)
        w1 = tk.Spinbox(master, textvariable=self.var, from_=f, to=t)
        w1.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
    
#    def myflags(self):
#        return ['-'+self.flg, str(self.var.get())]
        
class bvar(ifrow):
    """Boolean input (Checkbox) in interface"""
    def __init__(self, master, cfgline):
        ifrow.__init__(self, master,cfgline)   # init superclass
        self.flg = cfgline.flag
        self.var = tk.BooleanVar()
        self.default = cfgline.default=="ticked"
        self.var.set(self.default)
        w1 = ttk.Checkbutton(master, variable=self.var)
        w1.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
    
#    def myflags(self):
#        return self.flg, self.var.get()
        
class cvar(ifrow):
    """choice input (???) in interface"""
    def __init__(self, master, cfgline):
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.flg = cfgline.flag
        self.opt = cfgline.constraint.split(';')
        w1 = tk.Listbox(master, height=2)
        self.var = w1
        for x in self.opt:
            w1.insert(tk.END, x)
        # find the default position
        sel = 0
        for n, x in enumerate(self.opt):
            if cfgline.default==x:
                sel = n
        self.default = sel
        w1.selection_set(sel)
        w1.see(sel)
        w1.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
    
    def myflags(self):
        csel = self.var.curselection()[0]
        # print(self.flg, "flag is", csel)
        return self.flg, self.opt[csel]

class fvar(ifrow):
    """File input in interface - with browse buttin, calls file dialog"""
    def __init__(self, master, cfgline):
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.label = cfgline.label
        self.flg = cfgline.flag
        self.var = tk.StringVar()
        self.default = None
        self.required = cfgline.constraint=="required"
        w1 = ttk.Entry(master, textvariable=self.var, width=80)
        w1.grid(row=master.rows, column=1, sticky='w')
        # I can't get .fq.gz to work ... just put .gz in the allowed extentions?
        # self.ft = [('FASTQ file', x+z) for x in cfgline.default.split(';') for z in ['', '.gz']]
        self.ft = [('FASTQ file', x) for x in cfgline.default.split(';')]
        def varset():
            fn = tkFileDialog.askopenfilename(title=self.label, filetypes=self.ft)
            self.var.set(fn)
            return
        w2 = ttk.Button(master, text="Browse", command=varset )
        w2.grid(row=master.rows, column=2 )
        master.rows += 1
        return
    
    def myflags(self):
        s = self.var.get()
        if self.required and not s:
            tkMessageBox.showerror("Missing filename", "Please select a filename for\n%s." % self.label)
            raise Exception, "Missing filename."
        return self.flg, s
        

class pipesect(ttk.Frame):
    """extend the ttk.LabelFrame for a pileline section in the user interface"""
    def __init__(self, master, label):
        assert label     # our LabelFrames must have a name ...
        ttk.Frame.__init__(self, master, borderwidth=2, relief="raised", style="M.TFrame")
        self.pack(fill='x', padx=5, pady=5, ipadx=5) # should increment row ...
        self.label = label
        self.master = master
        self.vars = [] # a list of ifrows
        l = ttk.Label(self, text=label, width=18, style="M.TLabel")
        l.grid(row=0, column=0)
        self.rows = 1
        return
    
    def getflags(self):
        return self.label, dict(a.myflags() for a in self.vars)
    
class App(ttk.Frame):
    """
    GUI for Forensics pipeline
    
    Uses Tkinter so it runs on a standard Python installation ... 
    no extra modules needed.
    """
    
    def run(self):
        "collect the arguments from the GUI widgets and call the processing function"
        # OK ... it's time to do the work!
        status('Doing Run button.')
        try:
            argdict = dict(f.getflags() for f in self.fv)
            code.run_pipeline(argdict)
            status('Done Run.')
        except:
            status('Run failed.')        
        return
        
    def __init__(self, master, cfgfn):
        "set up the UI from the configuration file"
        global __progname__, __version__, __imagedata__, status
        
        sx=ttk.Style()
        sx.configure("M.TLabel", foreground='darkblue', font="Georgia 14 italic" )
        sx.configure("M.TFrame", foreground='green', font="Georgia 14 italic", background="palegoldenrod" )
        sx.configure("R.TButton", background="gray")
        sx.map("R.TButton", background=[("disabled", "yellow"), ("active", "red")])
        
        ttk.Frame.__init__(self, master, border=5)
        mx = ttk.Frame()
        mx.pack(ipadx=10, ipady=10)
                
        wfunc = {'tickbox': bvar, 'int': ivar, 'file': fvar, 'choice': cvar}

        cfglabs = ['group', 'flag', 'label', 'type', 'constraint', \
                        'default', 'mouse_over' ]
        cfglen  =len(cfglabs)
        Cfgline = collections.namedtuple('Cfgline', cfglabs)
        
        self.fv = []    # Frames vector/list - needed to get pipe-section arguments
        
        # read the configuration file
        # there's a header line, then a series of lines describing the App parameters.
        # It's a TAB separated file. Fields vary a bit depending on the value type.
        # The differences are handled by the various subclasses of class ifrow above ...
        # the wfunc dict maps row types to subclass constructors
        
        with open(cfgfn) as inp:
            lxfirst, m = True, None
            for lx in inp:
                lxs = lx.rstrip()
                if lxs=='' or lxs.startswith('#'): # drop comment or blank rows
                    continue
                fld = lxs.split("\t")
                if lxfirst: # skip the header line
                    assert len(fld)==cfglen     # check that the CFG file has the right number of fields
                    lxfirst = False
                    continue
                if not (m and m.label==fld[0]): # column 0? Start a new pipe-section ... 
                    m = pipesect(mx, fld[0])    # start a new pipe section
                    self.fv.append(m)           # add this pipe-section to the frames-vector
                    
                if len(fld)<cfglen:
                    fld += [None]*(cfglen-len(fld))
                assert len(fld)==cfglen
                cfg = Cfgline(*tuple(fld))  # make named tuple from config line
                wfunc[cfg.type](m, cfg)     # generate the parameter line in the GUI
        
        status("done reading config file.")
        w = ttk.Button(mx, text="Run", style="R.TButton", command=self.run)
        w.pack(pady=10)
        status("made 'Run' button.")
        
        # the GUI ... 
        # self.img = tk.PhotoImage(data=__imagedata__)    # this must be kept in memory!
        # del __imagedata__   # dispose of the big string!
        
        # make a status bar at the bottom
        # using tk (instead of ttk) so we can set the colour ... can't get ttk styles to work
        
        sc = "peachpuff" # status background colour
        sf = tk.Frame(master, background=sc, border=2, relief="sunken")
        sf.pack(fill=tk.X, padx=5, pady=5)
        sblab = tk.Label(sf, text="status:", border=2, background=sc)
        sblab.pack(side=tk.LEFT)
        
        
        self.sbvar = tk.StringVar()
        self.sbprev ="\n"
        self.sb = tk.Label(sf, textvariable=self.sbvar, background=sc)
        self.sb.pack(fill=tk.X, side=tk.LEFT)
        def setsb(*txt, **kw):
            res = ''
            if self.sbprev=="":
                res = self.sbvar.get()
            self.sbprev = kw["end"] if "end" in kw else "\n"
            for s in txt:
                res += ' '+str(s)
            self.sbvar.set(res)
            self.update()
            return
        status = setsb
        status("awaiting user activity.")
        return 
        
def win():
    """GUI version - main program"""      
    global __progname__
    root = tk.Tk()
    root.title(__progname__)
    app = App(root, 'cfg.tab')
    app.mainloop()
    root.quit()
    return

def ignore (*args, **kw):
    return
    
if __name__ == "__main__":
    status (sys.argv[0], 'starting.')
    ## embed
#    import base64
#    with open('getcore.gif','rb') as src:    
#        __imagedata__ = base64.b64encode(src.read())
    win()
       
