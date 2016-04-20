# -*- coding: utf-8 -*-

"""
A combination widget to display both a text status
and a progress bar.

based on Tkinter and ttk widgets ...
"""

import Tkinter as tk
import ttk

class StatusProgress(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master)
        
        self.sbvar = tk.StringVar()
        self.lab = ttk.Label(self, textvariable=self.sbvar)
        self.lab.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.pb  = ttk.Progressbar(self)
        self.pb.pack(fill=tk.X)
        return
    
    def start(self, *args, **kw):
        self.pb.start(*args, **kw)
        return
        
    def step(self, *args, **kw):
        self.pb.step(*args, **kw)
        return
        
    def stop(self, *args, **kw):
        self.pb.stop(*args, **kw)
        return
        
    def end(self):
        pb = self.pb
        pb["value"] = pb["maximum"]
        return

        
    def status(self, *args):
        self.sbvar.set(' '.join(str(x) for x in args))
        self.lab.update()
        return
