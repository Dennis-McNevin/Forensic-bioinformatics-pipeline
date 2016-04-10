# -*- coding: utf-8 -*-

import Tkinter as tk

def Display(event, c=' '):
    global pup
    w = event.widget
    print c+':', "popping up for", event.type
    if 'text' not in w.keys():
        return
    print "w[text] =", w['text']
    pup.pupmsg.set(w.popup)
    pup.state("normal")
    return "break"
    
def Remove(event):
    global pup
    w =event.widget
    print '  leaving -- type =', event.type
    if 'text' not in w.keys():
        return
    print "leaving", w['text']
    pup.pupmsg.set('')
    pup.state("withdrawn")
    return "break"

class MyApp(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.grid()

        self.l1 = tk.Label(self, text='testing', width=60, bg='lightblue')
        self.l1.popup ="hovering over Label#1"
        self.l1.bind("<Enter>", lambda e: Display(e, '1'))
        self.l1.bind("<Leave>", Remove)
        self.l1.grid(padx=20, pady=20, ipadx=10, ipady=5)
          
        self.l2 = tk.Label(self, text='Label 2 - a second hover region', bg='lightgreen')
        self.l2.popup = "hover info. for Label #2 - :)"
        self.l2.bind("<Enter>", lambda e: Display(e, '2'))
        self.l2.bind("<Leave>", Remove)
        self.l2.grid(padx=20, pady=20, ipadx=20, ipady=15)        

        global pup
        pup = tk.Toplevel(bg="lightyellow")
        pup.pupmsg = tk.StringVar()
        pup.puplab = tk.Label(pup, textvariable=pup.pupmsg, bg="lightyellow", width=40)
        pup.puplab.pack(padx=10, pady=10)
        
        pup.transient(self)
        pup.lower(self)
        pup.state("withdrawn")
        pup.overrideredirect(True)

        
        return      
 
app = MyApp()
app.master.title('test')
app.mainloop()