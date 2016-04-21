# -*- coding: utf-8 -*-

"""
A combination widget to display both a text status
and a progress bar.

based on Tkinter and ttk widgets ...
"""

import Tkinter as tk
import ttk

class StatusProgress(tk.Frame):
    """
    A GUI class that holds both a progress bar and a status message.
    It packs itself at the bootom of its parent frame.
    """
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master)
        
        self.sbvar = tk.StringVar()
        self.lab = ttk.Label(self, textvariable=self.sbvar)
        self.lab.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.pb  = ttk.Progressbar(self)
        self.pb.pack(fill=tk.X)
        return
    
    def start(self, *args, **kw):
        "pass through to progress bar"
        self.pb.start(*args, **kw)
        return
        
    def step(self, *args, **kw):
        "pass thropugh to progress bar"
        self.pb.step(*args, **kw)
        return
        
    def stop(self, *args, **kw):
        "pass through to progress bar"
        self.pb.stop(*args, **kw)
        return
        
    def end(self):
        "stop progress bar and display 100% (completed)"
        pb = self.pb
        pb.stop()
        pb["value"] = pb["maximum"]
        return

        
    def status(self, *args):
        "display a message in the status message ... works like print(...)"
        self.sbvar.set(' '.join(str(x) for x in args))
        self.lab.update()
        return
