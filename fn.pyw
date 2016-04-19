#!/usr/bin/env python
"""
    NGS Forensic GUI and Pipeline Caller
    author: Bob Buckley, ANU Bioinformatics Consultancy, 
        John Curtin School of Medical Research, Australian National University
    4-APR-2016
    
    This program imports the appPages module and uses its contents to build a
    user interface. There are multiple configuration files that describe pipeline
    pages in a "notebook" style interface.
    
    There's an initial home page.
    
    When the 'run' button is pressed, it calls an external procedure 
    that is set up in the appPages module. The demo appPages module uses the 
    dummy.py module. dummy.py shows how a pileline module is setup and can
    show it's progress and status in the GUI status region. 
    
    To do:
        - maybe add a menu bar
    
"""

from __future__ import print_function

__version__ = "0.1-a3"
__progname__ = "NGS Forensics Pipeline"

status = print
progbar = None

import platform
myos = platform.system()

import Tkinter as tk
import ttk
import tkFileDialog
import tkMessageBox
import collections
import subprocess

import appPages
import SplashScreen as ss 

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
        self.var = None
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
    
class cvar(ifrow):
    """Combobox - choice input in interface"""
    def __init__(self, master, cfgline):
        ifrow.__init__(self, master, cfgline)   # init superclass
        self.flg = cfgline.flag
        self.opt = cfgline.constraint.split(';')
        self.default = cfgline.default
        self.var = ttk.Combobox(master, values=self.opt, state="readonly")
        self.var.set(cfgline.default)
        self.var.grid(row=master.rows, column=1, sticky='w')
        master.rows += 1
        return
    
class fvar(ifrow):
    """File input in interface - with browse buttin, calls file dialog"""
    def __init__(self, master, cfgline):
        self.required = cfgline.constraint=="required"
        sz = "R.TLabel" if self.required else None
        ifrow.__init__(self, master, cfgline, style=sz)   # init superclass
        self.label = cfgline.label
        self.flg = cfgline.flag
        self.var = tk.StringVar()
        self.default = None
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
        ttk.Frame.__init__(self, master, borderwidth=2, relief="raised") # , style="M.TFrame")
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
        
class MyProgBar(ttk.Progressbar):
    "progress bar ... ends at maximum (no reset - call stop() to reset)"    
    def end(self):
        "show a completed progress bar"
        self["value"]=self["maximum"]
        self.update()
        return
        
    def step(self, x):
        "override step() ... that stops at the maximum value"
        mx = self["maximum"]
        self["value"] += x
        if self["value"]>=mx:
            self["value"] = mx
        # ttk.Progressbar.step(self, x)
        self.update()
        return
    
    def status(self, *args, **kw):
        "update the application's status message ... args are converted to strings."
        self.statfunc(*args, **kw)
        return
    
class Page(ttk.Frame):
    """
    A Notebook page for a Forensics pipeline
    """
    
    def __init__(self, nb, cfg):
        ttk.Frame.__init__(self, nb)    # border=?
        nb.add(self, text=cfg.tabname)  # instead of pack or grid
                
        wfunc   = {'tickbox': bvar, 'int': ivar, 'file': fvar, 'choice': cvar}

        cfglabs = ['group', 'flag', 'label', 'type', 'constraint', \
                        'default', 'mouse_over' ]
        cfglen  = len(cfglabs)
        Cfgline = collections.namedtuple('Cfgline', cfglabs)
        
        self.fv = []    # Frames vector/list - needed to get pipe-section arguments
        self.pipeline = cfg.run_pipeline
        
        # read the configuration file
        # there's a header line, then a series of lines describing the App parameters.
        # It's a TAB separated file. Fields vary a bit depending on the value type.
        # The differences are handled by the various subclasses of class ifrow above ...
        # the wfunc dict maps row types to subclass constructors
        
        with open(cfg.filename) as inp:
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
                    m = pipesect(self, fld[0])  # start a new pipe section
                    self.fv.append(m)           # add this pipe-section to the frames-vector
                    
                if len(fld)<cfglen:
                    fld += [None]*(cfglen-len(fld))
                assert len(fld)==cfglen
                cx = Cfgline(*tuple(fld))  # make named tuple from config line
                wfunc[cx.type](m, cx)      # generate the parameter line in the GUI
        
        status("done reading config file:", cfg.filename)
        # ttk.Separator(self, orient="horizontal").pack(pady=2)
        
        w = ttk.Button(self, text="Run", style="R.TButton", command=self.run)
        w.pack(pady=10)
        return

    def run(self):
        global status, progbar
        "collect the arguments from the GUI widgets and call the processing function"
        # OK ... it's time to do the work!
        # should disable the 'run' button?
        status('Doing Run button.')
        try:
            progbar.stop()  # resets to empty
            progbar.update()
            argdict = dict(f.getflags() for f in self.fv)
            status('Running ...')
            self.pipeline(argdict, progress=progbar)
            progbar.end()
            status('Done Run.')
        except:
            status('Run failed.')  
        # should re-enable the 'run' button ... ?
        return

def browseOpen(url):
    "fire up a browser with the help screen"
    global myos
    
    # need to get the following right for your system configuration.
    cmds = {
    'Darwin': "open -a 'Google Chrome.app' %s &",
    'Linux' : 'firefox %s &',
    'Windows': 'echo no help with %s here.'
    }

    subprocess.call(cmds[myos]%url, shell=True)
    return
    
class HomePage(ttk.Frame):
    """The Home tab ... pretty graphics and text."""
    def __init__(self, nb):
        ttk.Frame.__init__(self, nb, border=2)
        nb.add(self, text="Home")
        
        tm = """This forensics bioinfomatics pipeline was jointly funded by the US Defence Forensics Science Centre and the Department of Army Research,
Development and Engineering Command (ITC-PAC). It was developed by the National Centre for Forensic Studies at the University of Canberra in
collaboration with: Australian National University, Bioinformatics Consultancy; Victoria Police Forensic Services Department (Office of the
Chief Forensic Scientist); NSW Forensic and Analytical Science Service; Australian Federal Police (Forensics)"""
        
        self.img1 = tk.PhotoImage( master=self, file="pix/welcome_image_sm.gif" )
        self.img2 = tk.PhotoImage( master=self, file="pix/welcome_ncfs_sm.gif" )
        self.img3 = tk.PhotoImage( master=self, file="pix/welcome_uc_sm.gif" )
        
        ttk.Label(self, image=self.img1, style="HP.TLabel").pack()
        ttk.Label(self, text=tm, style="HP.TLabel").pack(ipady=10, ipadx=5)
        f1 = ttk.Frame(self)
        f1.pack(padx=30)
        ttk.Button(f1, text="About", command=lambda : browseOpen("about.html")).pack(side=tk.LEFT, pady=20)
        ttk.Button(f1, text="Help", command=lambda : browseOpen("help.html")).pack(side=tk.LEFT, pady=20)
        ttk.Button(f1, text="STR Browser", command=lambda : browseOpen("http://localhost:3000/")).pack(side=tk.LEFT, pady=20)
        f2 = ttk.Frame(self)
        f2.pack()
        ttk.Label(f2, image=self.img2, style="HP.TLabel").pack(side=tk.LEFT, padx=10)
        ttk.Label(f2, image=self.img3, style="HP.TLabel").pack(side=tk.LEFT, padx=10)       
        
        return
    
                
Cfgs = collections.namedtuple('Cfgline', ["tabname", "filename", "run_pipeline"])

class App(ttk.Frame):
    """Forensics Application
    
    This app uses a ttk.Notebook at the top level.
    Each Notebook pages collects parameters and runs a pipeline application (that
    is it calls its own python run_pipeline() procedure).
    """
    
    def __init__(self, master):
        "set up the UI for the whole Notebook"
        global __progname__, __version__, __imagedata__, status, progbar, progvar
        
        ttk.Frame.__init__(self, master, border=2)
        
        sx=ttk.Style()
        sx.configure(".", font="Ariel 12")
        sx.configure("M.TLabel", foreground='darkblue', font="Georgia 14 italic" )
        sx.configure("R.TLabel", foreground="black", font="Ariel 12 bold")  # for required fields
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
        pup.puplab.pack(padx=10, pady=10)
        
        pup.transient(self)
        pup.lower(self)
        pup.state("withdrawn")

        # create a Notebook for the Application ... 
        nb = ttk.Notebook(master)
        nb.pack(padx=5, pady=5)
        
        # make a progress bar and a status bar at the bottom
        # using tk (instead of ttk) so we can set the colour ... 
        # can't get ttk styles to work sufficiently on a Mac
        pb = MyProgBar(master, mode='determinate',
                             orient=tk.HORIZONTAL)
        pb.pack(fill=tk.X, padx=5, pady=5)
        progbar = pb
        
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
            res = self.sbvar.get() if self.sbprev=="" else ''
            self.sbprev = kw["end"] if "end" in kw else "\n"
            if res:
                res += ' '
            res += ' '.join(str(s) for s in txt)    # make into strings and append
            self.sbvar.set(res)
            self.update()
            return
        pb.statfunc = setsb

        status = setsb
        
        # setup Notebook pages
        HomePage(nb)
        for xargs in appPages.pages:
            Page(nb, Cfgs(*xargs))
            
        status("awaiting user activity.")
        return
        
def win():
    """GUI version - main program"""      
    global __progname__
    root = tk.Tk()
    root.title(__progname__)
    
    ss.SplashScreen(root, imageFilename='my.gif', text="NGS Forensics Pipelines",
                    progbar=True, start=appPages.main)
    app = App(root)
    app.mainloop()
    root.quit()
    return

def ignore (*args, **kw):
    return
    
if __name__ == "__main__":
    ## embed
#    import base64
#    with open('getcore.gif','rb') as src:    
#        __imagedata__ = base64.b64encode(src.read())
    win()
