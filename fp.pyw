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
        - display progress ... in a progress bar? 
        - command logging ... to enhance result reproducibility
        - maybe make a button to make advanced options visible?
    
"""

from __future__ import print_function

__version__ = "0.1-a1"
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
        self.default = False
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
        # I can't get .gq.gz to work ... just put .gz in the allowed extentions?
        # self.ft = [('FASTQ file', x+z) for x in cfgline.default.split(';') for z in ['', '.gz']]
        self.ft = [('FASTQ file', x) for x in cfgline.default.split(';')]
        def varset():
            fn = tkFileDialog.askopenfilename(filetypes=self.ft)
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
        

class pipesect(ttk.LabelFrame):
    """extend the ttk.LabelFrame for a pileline section in the user interface"""
    def __init__(self, master, label):
        assert label     # our LabelFrames must have a name ...
        ttk.LabelFrame.__init__(self, master, text=label)
        self.pack(fill='x', pady=15) # should increment row ...
        self.label = label
        self.master = master
        self.vars = [] # a list of ifrows
        self.rows = 1
        return
    
    def getflags(self):
        return self.label, dict(a.myflags() for a in self.vars)
    
class App(ttk.Frame):
    """GUI for Forensics pipeline
    
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
        # sx.theme_use('default')
        sx.configure("X.TLabelframe", foreground='blue', background='gray')
        sx.configure("X.TLabelframe", font="Georgia 18")
#        print("sx.theme_names() =", sx.theme_names())
#        print("sx.theme_use() =", sx.theme_use())
#        print("element_options =", sx.element_options('Tlabelframe'))
#        print("element_options (.label) =", sx.element_options('Tlabelframe.label'))
#        print("lookup fg =", sx.lookup('X.TLabelframe', 'foreground'))
#        print("lookup font =", sx.lookup('X.TLabelframe', 'font'))
#        print("layout X.TLabelframe=", sx.layout('X.TLabelframe'))
        # print("layout TButton=", sx.layout('TButton'))
        
        ttk.Frame.__init__(self, master)
        mx = ttk.Frame()
        #mx.grid(row=0, column=0)
        #master.grid()
        mx.pack()
                
        # wfunc = { 'button': ttk.Button, 'label': ttk.Label, 'entry': ttk.Entry, 'cb': ttk.Checkbutton }
        wfunc = {'tickbox': bvar, 'int': ivar, 'file': fvar, 'choice': cvar}
        
        Cfgline = collections.namedtuple('Cfgline', ['group', 'flag', 'label', 'type', 'constraint', \
                        'default', 'mouse_over' ])
        
        # self.tvars, self.bvars, self.ivars, self.tflags, self.bflags, self.iflags = [], [], [], '', '', ''
        self.fv = []    # list of LabelFrames - needed to get pipesection arguments
        with open(cfgfn) as inp:
            lxfirst, m = True, None
            for lx in inp:
                if lx.lstrip().startswith('#'): # drop comment rows
                    continue
                if lxfirst: # skip the header line
                    lxfirst = False
                    continue
                fld = lx.rstrip().split("\t")
                if not (m and m.label==fld[0]):  # column 0? Start a new labelFrame ... 
                    # m = tk.LabelFrame(mx, text=fld[0], borderwidth=5, fg='blue', bg='#eeeeee')
                    # sx.theme_use("aqua")
                    m = pipesect(mx, fld[0])
                    self.fv.append(m)
                    m['borderwidth'] = 2
                    
                    # m = ttk.LabelFrame(mx, text=fld[0], borderwidth=2, relief='raised', 
                    # style="X.TLabelframe")
#                    print("style=", m.winfo_class())
#                    print("sx.theme_use() =", sx.theme_use())
                    # m.configure(style="Blue.TLabelframe")
                    # m.grid(row=mr, column=0, sticky='we', ipadx=10, ipady=10)
                    # sx.theme_use('default')

                # print("fld[2]=", fld[2])
                if len(fld)<7:
                    fld += [None]*(7-len(fld))
                assert len(fld)==7
                cfg = Cfgline(*tuple(fld))
                wfunc[cfg.type](m, cfg)
        
        status("read config file.")
        w = ttk.Button(mx, text="Run", command=self.run)
        # w.grid(row=mr, column=0, padx='20', pady='15', sticky='w')
        # w.grid(row=mr, column=0, pady=15)
        w.pack(pady=15)
        status("done 'Run' button.")
        
        
        
        
        # the GUI ... so in self.run() above we can easily get a namedtuple of value
        # self.img = tk.PhotoImage(data=__imagedata__)    # this must be kept in memory!
        # del __imagedata__   # dispose of the big string!
        
        self.sbvar = tk.StringVar()
        self.sbprev ="\n"
        self.sb = ttk.Label(master, textvariable=self.sbvar)
        #self.sb.grid(row=mr, sticky='w', columnspan=5)
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
       
