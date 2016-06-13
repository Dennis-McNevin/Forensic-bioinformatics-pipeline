#!/usr/bin/env python
"""
    MPS Forensic GUI and Pipeline Caller
    author: Bob Buckley, ANU Bioinformatics Consultancy, 
        John Curtin School of Medical Research,
        Australian National University
    4-APR-2016
    
    This program imports the appPages module and uses its contents to build a
    user interface. There are multiple configuration files that describe pipeline
    pages in a "notebook" style interface.
    
    The notebook has an initial home page.
    
    When the 'run' button is pressed, it calls an external procedure 
    that is set up in the appPages module. The demo appPages module uses the 
    dummy.py module. dummy.py shows how a pileline module is setup and can
    show it's progress and status in the GUI status region. 
    
    There's splash screen that allows startup code to run in the background ... 
    see dummystart.py
"""

from __future__ import print_function

__version__ = "0.1-b2"
__progname__ = "MPS Forensics"

progbar = None  # global variable - for the application's progress bar

import platform
myos = platform.system()
import os
import sys
cwd = None

import Tkinter as tk
import ttk
import tkFileDialog
import tkMessageBox
import collections
import subprocess

import SplashScreen as ss
import StatusProgress as sp 


def Display(event):
    "<Enter> callback to display popup/tooltip"
    global pup
    w = event.widget
    if 'text' not in w.keys():
        return
    pup.geometry("+%d+%d" % (event.x_root, event.y_root-50))
    pup.pupmsg.set(w.popup)
    pup.state("normal")
    return "break"
    
def Remove(event):
    "<Leave> callback for labels"
    global pup
    w =event.widget
    if 'text' not in w.keys():
        return
    pup.pupmsg.set('')
    pup.state("withdrawn")
    return "break"

class ifrow:
    """
    Superclass for an Interface row.
    
    Every row has a label ... so handle it here.
    """
    def __init__(self, master, cfgline, style=None):
        self.flg = cfgline.flag
        self.default = cfgline.default
        w0 = ttk.Label(master, text=cfgline.label)
        if style:
            w0["style"] = style
        w0.grid(row=master.rows, column=0, sticky='e')
        master.vars.append(self)

        # if there is a mouse_over string, then remember it and
        # bind <Enter> and <Leave> callbacks.
        if cfgline.mouse_over:
            w0.popup = cfgline.mouse_over
            w0.bind("<Enter>", Display)
            w0.bind("<Leave>", Remove)

        return
    
    def myflags(self):
        "return the flag and its value"
        return self.flg, self.var.get()
    
class ivar(ifrow):
    """Integer input in interface"""
    def __init__(self, master, cfgline):
        self.var = tk.StringVar()
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.var.set(self.default)
        try:
            f,t = cfgline.constraint.rsplit('-',1) # rsplit allow initial negative number
        except ValueError:
            print("Ugh, bad config line:", cfgline)
            raise ValueError
        w1 = tk.Spinbox(master, textvariable=self.var, from_=f, to=t)
        w1.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
        
class gvar(ifrow):
    """Float input in interface
    The constaint option has a 3rd value - the number of digits after the decimal point"""
    def __init__(self, master, cfgline):
        self.var = tk.StringVar()
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.var.set(self.default)
        f,t,d = cfgline.constraint.split('-')
        d=int(d)
        w1 = tk.Spinbox(master, textvariable=self.var, from_=float(f), to=float(t),
                        format='%%.%df'%d, increment=float('.'+'0'*(d-1)+'1'))
        w1.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
       
class tvar(ifrow):
    """Text input in interface"""
    def __init__(self, master, cfgline):
        self.var = tk.StringVar()
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.var.set(self.default)
        w1 = tk.Entry(master, textvariable=self.var, width=max(20, int(cfgline.constraint)))
        w1.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
    
class bvar(ifrow):
    """Boolean input (Checkbox) in interface"""
    def __init__(self, master, cfgline):
        self.var = tk.BooleanVar()
        ifrow.__init__(self, master,cfgline)   # init superclass
        self.default = cfgline.default.startswith("tick")
        self.var.set(self.default)
        w1 = ttk.Checkbutton(master, variable=self.var)
        w1.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
    
class cvar(ifrow):
    """Combobox - choice input in interface"""
    def __init__(self, master, cfgline):
        opt = cfgline.constraint.split(';')
        self.var = ttk.Combobox(master, values=opt, state="readonly")
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.var.set(cfgline.default)
        self.var.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
    
class fvar(ifrow):
    """File input in interface - with browse button, calls file dialog"""
    def __init__(self, master, cfgline, dirflag=False):
        self.var = tk.StringVar()
        self.required = cfgline.constraint=="required"
        sz = "R.TLabel" if self.required else None
        ifrow.__init__(self, master, cfgline, style=sz)   # init superclass
        self.label = cfgline.label	# used for dialog titles
        self.default = None
        w1 = ttk.Entry(master, textvariable=self.var, width=80)
        w1.grid(row=master.rows, column=1, sticky='w')
        # I can't get .fq.gz to work ... just put .gz in the allowed extentions?
        # self.ft = [('FASTQ file', x+z) for x in cfgline.default.split(';') for z in ['', '.gz']]
        if dirflag:
            self.var.set(cfgline.default)
        else:
            self.ft = [('File', x) for x in cfgline.default.split(';')]
        def fileset():
            fn = tkFileDialog.askopenfilename(title=self.label, filetypes=self.ft)
            self.var.set(fn)
            return
        def dirset():
            fn = tkFileDialog.askdirectory(title=self.label)
            self.var.set(fn)
            return
        w2 = ttk.Button(master, text="Browse", command=dirset if dirflag else fileset )
        w2.grid(row=master.rows, column=2 )
        master.rows += 1
        return
    
    def myflags(self):
        "return the flag and its value - message and raise an exception if a required value is absent"
        s = self.var.get()
        if self.required and not s:
            tkMessageBox.showerror("Missing filename", "Please select a filename for\n%s." % self.label)
            raise Exception, "Missing filename."
        return self.flg, s        

class pipesect(ttk.Frame):
    """extend the ttk.LabelFrame for a pileline section in the user interface"""
    def __init__(self, master, label, labtext):
        assert label     # our LabelFrames must have a name ...
        ttk.Frame.__init__(self, master, borderwidth=2) # , style="M.TFrame")
        self.pack(fill=tk.X, ipadx=5, ipady=2) # should increment row ...
        self.label = label
        self.master = master
        self.vars = [] # a list of ifrows
        l = ttk.Label(self, text=labtext, width=18, style="M.TLabel")
        l.grid(row=0, column=0)
        self.rows = 1
        return
    
    def getflags(self):
        "get the label and a Python dictionary of flags and their values"
        return self.label, dict(a.myflags() for a in self.vars)
        
class Page(ttk.Frame):
    """
    A Notebook page for a Forensics pipeline
    """
    
    def __init__(self, nb, cfg):
        ttk.Frame.__init__(self, nb)    # border=?
        nb.add(self, text=cfg.tabname)  # instead of pack or grid
                
        wfunc   = {'tickbox': bvar, 'int': ivar, 'float': gvar,
                    'text': tvar, 'file': fvar, 'choice': cvar,
                    'directory': (lambda m, cfg: fvar(m, cfg, dirflag=True)) }

        cfglabs = ['group', 'grouplab', 'flag', 'label', 'type', 'constraint', \
                        'default', 'mouse_over' ]
        cfglen  = len(cfglabs)
        Cfgline = collections.namedtuple('Cfgline', cfglabs)
        
        self.fv = []    # Frames vector/list - needed to get pipe-section arguments
        self.pipeline = cfg.run_pipeline
        
        # read the configuration file for this notebook page and it's associated pipeline code
        # there's a header line, then a series of lines describing the pipeline's parameters.
        # It's a TAB separated file. Fields vary a bit depending on the value type.
        # The differences are handled by the various subclasses of class ifrow above ...
        # the wfunc dict maps row types to subclass constructors
        
        fs = [(self, cfg.filename)]
        
        # create a Notebook if its needed for complex options
        nbx = None
        if cfg.subtabs:
            nbx = ttk.Notebook(self)
            for p in cfg.subtabs:
                nbxf = ttk.Frame(nbx)
                nbx.add(nbxf, text=p[0])
                fs.append((nbxf, p[1]))
        
        # run though the configuration file(s) building the GUI for the pipelines
        # Note: there is still just one frame-vector with argument widgets
        # so just one dictionary is passed as a parameter to the pipeline (there is
        # one Run button for each pipeline)
        for myf, fnx in fs:
            fn = fnx if fnx.startswith(os.path.sep) else os.path.join(cwd, fnx)
            progbar.status("start reading config file:", fn)
            with open(fn) as inp:
                # fldprev is fields from the previous row ... value replace blank fields
                # popts is the pipeline options section being constructed
                fldprev, popts = [None]*cfglen, None
                for lx in inp:
                    lxs = lx.rstrip()
                    if lxs=='' or lxs.lstrip().startswith('#'): # drop comment or blank rows
                        continue
                    fld = lxs.split("\t")
                    if len(fld)<cfglen:
                        fld += [None]*(cfglen-len(fld))
                    for i, fx in enumerate(fld):
                        if fx:
                            break
                        fld[i] = fldprev[i]
                    # fld = [fx if fx else prev for fx, prev in zip(fld, fldprev)]
                    assert len(fld)==cfglen, "fld is %r" % fld
                    cx = Cfgline(*tuple(fld))  # make named tuple from config line
                    if not (popts and popts.label==cx.group): # column 0? Start a new pipe-section ... 
                        popts = pipesect(myf, cx.group, cx.grouplab)  # start a new pipe section
                        self.fv.append(popts)           # add this pipe-section to the frames-vector
                        
                    if cx.type not in wfunc:	# report problem in config file
                        print()
                        print("In config. file:", fn)
                        print("   **** unknown option type:", cx.type)
                        print("type =", cx.type, cx)

                    assert cx.type in wfunc
                    try:
                        wfunc[cx.type](popts, cx)      # generate the parameter line in the GUI
                    except:
                        print("Bad option config:", cx)
                        progbar.status("Configuration error. :(")
                        raise
                    fldprev = fld
        
            progbar.status("done reading config file:", fn)
        
        # wait to now to pack the inner notebook ... if it exists.
        if nbx:
            #nbx.pack(fill=tk.BOTH)
            nbx.pack()
        
        self.runButton = ttk.Button(self, text="Run", style="R.TButton", command=self.run)
        self.runButton.pack(pady=5)
        return

    def run(self):
        global progbar
        "collect the arguments from the GUI widgets and call the processing function"
        # OK ... it's time to do the work!
        self.runButton.configure(state=tk.DISABLED)
        progbar.status('start running.')
        #try:
        if 1:
            progbar.stop()  # resets to empty
            progbar.update()
            argdict = dict(f.getflags() for f in self.fv)
            progbar.status('running ...')
            self.pipeline(argdict, progress=progbar)
            progbar.end()
            progbar.status('Done.')
        #except:
        else:
            progbar.status('Run failed.')  
        self.runButton.configure(state=tk.NORMAL)
        return

def browseOpen(url):
    "fire up a browser window/tab with the specified URL open"
    global myos, cwd
    
    # need to get the following right for your system configuration.
    cmds = {
    'Darwin': "cd " + cwd + " ; open -a 'Google Chrome.app' %s &",
    'Linux' : "cd " + cwd + ' ; firefox %s &',
    'Windows': 'echo no help with %s here.'
    }

    subprocess.call(cmds[myos]%url, shell=True)
    return
    
class HomePage(ttk.Frame):
    """The Home tab ... pretty graphics and text."""
    def __init__(self, nb):
        global cwd
        ttk.Frame.__init__(self, nb, border=2)
        nb.add(self, text="Home")
        
        tm = """This forensics bioinfomatics pipeline was jointly funded by the US Defence Forensics Science Centre and the Department of Army Research,
Development and Engineering Command (ITC-PAC). It was developed by the National Centre for Forensic Studies at the University of Canberra in
collaboration with: Australian National University, Bioinformatics Consultancy; Victoria Police Forensic Services Department (Office of the
Chief Forensic Scientist); NSW Forensic and Analytical Science Service; Australian Federal Police (Forensics)"""
        
        self.img1 = tk.PhotoImage( master=self, file=os.path.join(cwd, "pix", "welcome_image_sm.gif") )
        self.img2 = tk.PhotoImage( master=self, file=os.path.join(cwd, "pix", "welcome_ncfs_sm.gif") )
        self.img3 = tk.PhotoImage( master=self, file=os.path.join(cwd, "pix", "welcome_uc_sm.gif") )
        
        ttk.Label(self, image=self.img1, style="HP.TLabel").pack(pady=5)
        ttk.Label(self, text=tm, style="HP.TLabel").pack(ipady=10, ipadx=5)
        f1 = ttk.Frame(self)
        f1.pack(padx=30)
        ttk.Button(f1, text="About", command=lambda : browseOpen("file://"+cwd+"/help/about.html")).pack(side=tk.LEFT, pady=20, padx=50)
        helpname = os.path.join(cwd, "help/help.html")
        if os.path.isfile(helpname): # no button unless the help file exists
            ttk.Button(f1, text="Help", command=lambda : browseOpen("file://"+helpname)).pack(side=tk.LEFT, pady=20, padx=50)
        else:
            print("No file:", helpname)
        ttk.Button(f1, text="STR Browser", command=lambda : browseOpen("http://localhost:3000/")).pack(side=tk.LEFT, pady=20, padx=50)
        f2 = ttk.Frame(self)
        ttk.Label(f2, image=self.img2, style="HP.TLabel").pack(side=tk.LEFT, padx=10)
        ttk.Label(f2, image=self.img3, style="HP.TLabel").pack(side=tk.LEFT, padx=10)       
        f2.pack(pady=5)
        
        return
    
                
Cfgs = collections.namedtuple('Cfgline', ["tabname", "filename", "run_pipeline", "subtabs"])

class App(ttk.Frame):
    """Forensics Application
    
    This app uses a ttk.Notebook at the top level.
    Each Notebook pages collects parameters and runs a pipeline application (that
    is it calls its own python run_pipeline() procedure).
    """
    
    def __init__(self, master, appPages):
        "set up the UI for the whole Notebook"
        global __progname__, __version__, __imagedata__, progbar
        
        ttk.Frame.__init__(self, master, border=2)
        
        sx=ttk.Style()
        sx.configure(".", font="Ariel 10")
        sx.configure("M.TLabel", foreground='darkblue', font="Georgia 12 italic" )
        sx.configure("R.TLabel", foreground="black", font="Ariel 10 bold")  # for required fields
        sx.configure("HP.TLabel", background="white", foreground="darkblue", font="Ariel 10 italic")
        sx.map("R.TButton", background=[("disabled", "salmon"), ("active", "yellowgreen")])
        # sx.configure("TNotebook", background="salmon")
        
        # create a withdrawn toplevel widget to display the tooltips
        global pup
        pup = tk.Toplevel(bg="lightyellow") # maybe set the geometry as well ... 
        pup.overrideredirect(1) # this is meant to remove the window decoration
        pup.pupmsg = tk.StringVar()
        pup.puplab = tk.Label(pup, textvariable=pup.pupmsg, bg="lightyellow", 
                              width=60, wraplength=600 ) # these may not be right
        pup.puplab.pack(padx=10, pady=5)
        
        pup.transient(self)
        pup.lower(self)
        pup.state("withdrawn")
        
        # make a progress bar and a status bar at the bottom
        pb = sp.StatusProgress(master, mode='determinate', orient=tk.HORIZONTAL)
        progbar = pb
        pb.pack(padx=5, pady=5, fill=tk.X, side=tk.BOTTOM)

        # create a Notebook for the Application ... 
        nb = ttk.Notebook(master)
        nb.pack(padx=5, pady=5)
        
        # setup Notebook pages
        HomePage(nb)
        for xargs in appPages.pages:
            # assert len(xargs)==4
            Page(nb, Cfgs(*xargs))
            
        pb.status("")
        return
        
def win(pages):
    """GUI version - main program"""      
    global __progname__, cwd, cmd
    cwd, cmd = os.path.split(sys.argv[0])
    if not cwd:
        cwd = os.getcwd()
    else:
        cwd = os.path.abspath(cwd)
    root = tk.Tk()
    root.title(__progname__)
    root.lift()
    root.wm_attributes("-topmost", 1)   # put at the front
    root.withdraw()
    
    ss.SplashScreen(imageFilename=os.path.join(cwd, 'pix/my.gif'), text="MPS Forensics Pipelines",
                    progbar=True, minSplashTime=pages.sstime, start=pages.main)
    
    app = App(root, pages)
    root.deiconify()
    root.wm_attributes("-topmost", 0)   # allow other windows at the front
    
    app.mainloop()
    root.quit()
    return

if __name__ == "__main__":
    import dummyapp as appPages
    win(appPages)
