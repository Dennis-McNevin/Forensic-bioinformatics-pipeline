# -*- coding: utf-8 -*-

import Tkinter as tk
import ttk

class VerticalScrolledFrame(tk.Frame):
    """Scrolled ttk Frame
    """
    
    def __init__(self, fp, *args, **kw):
        parent = ttk.Frame(fp)
        cnv = tk.Canvas(parent, relief="sunken", bd=3, bg="lightgreen")
        cnv.config(width=300, height=150)
        # cnv.config(scrollregion=cnv.bbox("all"))
        # cnv.config(scrollregion=(0, 0, 300, 1000))
        sb = ttk.Scrollbar(parent, orient=tk.VERTICAL)
        cnv.config(yscrollcommand=sb.set)
        sb.config(command=cnv.yview)
        sb.pack(fill=tk.Y, side=tk.RIGHT, padx=4, pady=4)
        cnv.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH, padx=4, pady=4)
        
        for i in range(10):
            cnv.create_text(150, 50+(i*100), text='label '+str(i+1))
        #cnv.xview_moveto(0)
        #cnv.yview_moveto(0)
        
#        kw["height"] = 150
#        kw["width"]  = 400
#        kw["relief"] = "groove"
        tk.Frame.__init__(self)
        cnv_id1 = cnv.create_window(10, 30, anchor=tk.NW)
        cnv.itemconfigure(cnv_id1, window=self)
        # self.pack()
        
        fx = ttk.Frame()
        cnv_id2 = cnv.create_window(250, 30, anchor=tk.NW)
        cnv.itemconfigure(cnv_id2, window=fx)
        
        lx = ttk.Label(text="My Label ...")
        cnv_id3 = cnv.create_window(120, 10, anchor=tk.NW, window=lx)
        
        ttk.Label(fx, text="foo").pack()
        ttk.Label(fx, text="my\nbaz").pack()

        parent.pack()
        self.wlist = [("canvas", cnv), ("lx", lx), ("fx", fx)]
        print "bbox =", cnv.bbox("all")
        
        def cnfcnv(event):
            print "in cnfcnv()", cnv.winfo_reqwidth(), cnv.winfo_width(), "pos=", event.x, event.y
            assert event.widget == cnv
            cnv.configure(scrollregion=cnv.bbox("all"))
            return
        cnv.bind('<Configure>', cnfcnv)
        
        return

    def px(self):
        for n,w in self.wlist:
            print n, "bbox =", w.bbox("all")
        return
        
        
if __name__=="__main__":
    root = tk.Tk()
    root.title("Testing ...")
    
    ttk.Label(root, text="Title line.\n...", justify=tk.CENTER).pack(expand=1)
    
    f = VerticalScrolledFrame(root)
    # f = ttk.Frame()
    ttk.Label(f, text="Inner label #1.").pack(pady=100)
    ttk.Label(f, text="inner label #2.").pack(pady=100)
    ttk.Label(f, text="Bottom label.", relief="groove", borderwidth=5).pack(pady=40)
    ttk.Button(root, text = "Huh").pack(side=tk.BOTTOM)
    
    print "big frame bbox =", f.bbox("all")
    f.px()
        
    root.mainloop()
    root.quit()