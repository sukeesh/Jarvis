from plugin import plugin

import numpy as np
import math
import tabula
@plugin("check slot for course")
#System.setProperty("sun.java2d.cmm", "sun.java2d.cmm.kcms.KcmsServiceProvider")
def helloworld(jarvis, s):
   # Read remote pdf into DataFrame
   df2 = tabula.read_pdf("http://www.iitmandi.ac.in/academics/files/Timetable_Aug-Dec2019.pdf", pages=2)
   arr=df2.get_values()
   #print(arr)
   count_row = df2.shape[0]  # gives number of row count
   t=0
   slot=0
   myDict={}
   for x in np.nditer(arr, flags=["refs_ok"], op_flags=["readwrite"]):
     if slot!=0:
          if x==x :
             myDict[(""+x)]=""+chr(slot+64)
     t=t+1
     if t==count_row:
          slot=slot+1
          t=0
   """Repeats what you type"""
   try:
        jarvis.say(myDict[s.upper()])
   except:
           jarvis.say("Course not found!!!")

    
