# -*- coding: utf-8 -*-

import Tkinter as tk
import time

class SplashScreen( object ):
   def __init__( self, tkRoot, imageFilename = None, text=None, minSplashTime=0 ):
      self._root              = tkRoot
      self._splash            = None
      self._minSplashTime     = time.time() + minSplashTime
      assert imageFilename
      print "reading", imageFilename
      self._image = tk.PhotoImage(master=self._root, file=imageFilename )
      
      tkRoot.after(int(minSplashTime*1000), self.finish)
      
      # Remove the app window from the display
      self._root.withdraw( )
      
      # Calculate the geometry to center the splash image
      scrnWt = self._root.winfo_screenwidth( )
      scrnHt = self._root.winfo_screenheight( )
      
      imgWt = self._image.width()
      imgHt = self._image.height()
      
      print "image: width =", imgWt, "height =", imgHt
      
      imgXPos = (scrnWt / 2) - (imgWt / 2)
      imgYPos = (scrnHt / 2) - (imgHt / 2) - 60 # a bit above centre

      # Create the splash screen      
      self._splash = tk.Toplevel()
      self._splash.overrideredirect(1)
      self._splash.geometry( '+%d+%d' % (imgXPos, imgYPos) )
      tk.Label( self._splash, image=self._image, cursor='watch' ).pack( )
      if text:
          tk.Label( self._splash, text=text ).pack()

      # Force Tk to draw the splash screen outside of mainloop()
      self._splash.update( )
      return
   
   def finish( self):
      # Make sure the minimum splash time has elapsed
      timeNow = time.time()
      if timeNow < self._minSplashTime:
         time.sleep( self._minSplashTime - timeNow )
      
      # Destroy the splash window
      self._splash.destroy( )
      
      # Display the application window
      self._root.deiconify( )
      if self._image:
          del self._image
      return


#--------------------------------------------
# Now putting up splash screens is simple



# Create the tkRoot window
r = tk.Tk( )

tm = "ForensiX by ANU Bioinformatics Consultancy"
SplashScreen( r, imageFilename='my.gif', text=tm,  minSplashTime=5 )

tk.Label(r, text="My application window", bg="lightgreen").pack(padx=20, pady=30)


r.mainloop( )
