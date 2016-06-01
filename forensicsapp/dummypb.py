"""
Dummy progress bar class
"""

class StatusProgress:
   def status(self, *args):
       print ' '.join(str(x) for x in args)
       return
   def end(self):
       print "Ended!"
       return
   def start(self, *args, **kw):
       return
   def step(self, *args, **kw):
       return
   def stop(self, *args, **kw):
       return
