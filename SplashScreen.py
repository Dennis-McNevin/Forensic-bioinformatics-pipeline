# -*- coding: utf-8 -*-
"""
Splash Screen module for Tkinter
Bob Buckley. ANU Bioinformatics Consultancy
   20-MAR-2016

Module to display an image in the middle of the screen
while an application starts up.
"""

import Tkinter as tk
import ttk
import StatusProgress as sp
import time

def geocentre(w, wid, hgt):
    sw = w.winfo_screenwidth()
    sh = w.winfo_screenheight()
    return "+"+str(int(sw/2-wid/2))+"+"+str(int(sh/2-hgt/2))
    

class SplashScreen(tk.Toplevel):
    def __init__( self, root, imageFilename=None, text=None, minSplashTime=3, 
                 progbar=False, start=None ):
        bd = 5  # bigger than default border
        tk.Toplevel.__init__(self, root, bd=bd, bg="black")
        self.overrideredirect(1)

        self.minSplashTime = time.time() + minSplashTime
        self.root = root
        assert imageFilename
        self.image = tk.PhotoImage(master=self, file=imageFilename )
        self.pb = None
      
        root.after(int(minSplashTime*1000), self.finish)
      
        # Remove the app window from the display
        root.withdraw( )
      
        # Calculate the geometry to center the splash image
        scrnWt = root.winfo_screenwidth( )
        scrnHt = root.winfo_screenheight( )
      
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
            self.pb = pb
            pb.start()

        # Force Tk to draw the splash screen outside of mainloop()
        self.update( )
        return
   
    def finish( self):
        # Make sure the minimum splash time has elapsed
        timeNow = time.time()
        if timeNow < self.minSplashTime:
            time.sleep( self.minSplashTime - timeNow )
        if self.pb:
            self.pb.stop()
      
        # Destroy the splash window
        self.destroy( )
      
        # Display the application window
        self.root.deiconify( )
        self.root.lift()
        
        if self.image:
            del self.image
        return

#--------------------------------------------
# Now putting up splash screens is simple

if __name__ == "__main__":
    # Create the tkRoot window
        
    r = tk.Tk( )
    
    tm = "ForensiX by ANU Bioinformatics Consultancy"
    mst=3
    ss = SplashScreen( r, imageFilename='my.gif', text=tm, minSplashTime=mst, progbar=True )
    mypb = ss.pb
    for i in range(mst):
        if mypb is not None:
            mypb.status("Step", i+1)
            mypb.step(33)
        time.sleep(1)
    ss.finish()
        
    r.geometry(geocentre(r, 600, 400))
    tk.Label(r, text="My application window", bg="lightgreen").pack(padx=20, pady=30)
    
    print "winfo: ", r.winfo_width(), r.winfo_height()
    
    r.mainloop( )
