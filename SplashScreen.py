# -*- coding: utf-8 -*-
"""
Splash Screen module for Tkinter and ttk
Bob Buckley. ANU Bioinformatics Consultancy
   20-MAR-2016

Module to display an image in the middle of the screen
while an application starts up.
"""

import Tkinter as tk
import ttk
import time
import StatusProgress as sp

def geocentre(w, wid, hgt):
    sw = w.winfo_screenwidth()
    sh = w.winfo_screenheight()
    return "+"+str(int(sw/2-wid/2))+"+"+str(int(sh/2-hgt/2))
    

class SplashScreen(tk.Toplevel):
    """
    Create and display a splash screen for an application.
    
    Using it's own Toplevel window.
    """
    
    def __init__( self, imageFilename=None, text=None, minSplashTime=5, 
                 bd=2, progbar=False, start=None ):
                     
        time0 = time.time()
        tk.Toplevel.__init__(self, None, bd=bd, bg="black")
        self.overrideredirect(1)

        self.minSplashTime = time.time() + minSplashTime
        assert imageFilename
        self.image = tk.PhotoImage(master=self, file=imageFilename )
        self.pb = None
      
        # Calculate the geometry to center the splash image
        scrnWt = self.winfo_screenwidth( )
        scrnHt = self.winfo_screenheight( )
      
        imgWt = self.image.width()
        imgHt = self.image.height()
      
        # print "image: width =", imgWt, "height =", imgHt
      
        imgXPos = (scrnWt / 2) - (imgWt / 2) - bd
        imgYPos = (scrnHt / 2) - (imgHt / 2) - bd - 60 # a bit above centre

        # Create the splash screen      
        self.geometry( '+%d+%d' % (imgXPos, imgYPos) )
        ttk.Label( self, image=self.image, cursor='watch' ).pack( )
        if text:
            ttk.Label( self, text=text ).pack(fill=tk.X)

        if progbar:
            pb = sp.StatusProgress(self, maximum=minSplashTime*20)
            pb.pack(fill=tk.X, side=tk.BOTTOM)
            self.pb = pb    # self.finish() uses this value
            # pb.start()
            
        self.front()
        
        # call the startup code - done while splash screen is displayed 
        if start:
            start(pb, Splash=self)
        
        self.front()

        # schedule splash screen finish() 
        tdiff = time.time() - time0
        self.after(max(int((minSplashTime-tdiff)*1000), 50), self.finalise)
        
        return
    
    def front(self):
        self.lift()
        self.wm_attributes("-topmost", 1)   # keep Spash Screen at the front?
        return
   
    def finalise(self):
        """Finish the splash screen.
        Then destroy the toplevel widget.
        """
        
        # stop the progress bar ... if it's running
        if self.pb:
            self.pb.end()
            self.pb.update()
        self.after(2000, self.finish)
        self.front()
        return

    def finish(self):
        # Destroy the splash window
        self.destroy( )
      
        if self.image:
            del self.image
        
        return

#--------------------------------------------
# Now putting up splash screens is simple

if __name__ == "__main__":
    
    def ssbg(mypb=None):
        steps=3
        for i in range(steps):
            if mypb is not None:
                mypb.status("Start step", i+1, "of", steps)
                mypb.step(33)
            time.sleep(1)
        mypb.status("Done.")
        return
    # Create a tkRoot window for the demo app
        
    r = tk.Tk( )
    r.lift()
    r.wm_attributes("-topmost", 1)   # put at the front    
    
    tm = "ForensiX by ANU Bioinformatics Consultancy"
    SplashScreen( imageFilename='my.gif', text=tm, minSplashTime=5, progbar=True, start=ssbg )
         
    r.geometry(geocentre(r, 600, 400))
    tk.Label(r, text="My application window", bg="lightgreen").pack(padx=20, pady=30)
    
    print "winfo: ", r.winfo_width(), r.winfo_height()

    r.wm_attributes("-topmost", 0)   # allow other windows at front      
    r.mainloop( )
