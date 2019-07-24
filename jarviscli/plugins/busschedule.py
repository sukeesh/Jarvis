
from plugin import LINUX, PYTHON3, plugin, require
import tabula
import time as t

@require(python=PYTHON3, platform=LINUX)
@plugin('busschedule')
def convert(s): 
  
    # initialization of string to "" 
    new = "" 
  
    # traverse in the string  
    for x in s: 
        new += x  
  
    # return string  
    return new 

def busschedule(jarvis, s):
    df2 = tabula.read_pdf("http://iitmandi.ac.in/files/inst_bus_schedule_12thjune2019.pdf", pages=2, multiple_tables=True)
    arr=df2[0].get_values()
    print(arr[8][3])
    ar=t.ctime().split(' ')
    systime=ar[3].split(':')
    flag=0
    for i in range(0,arr.shape[0]):
        for j in range(3):
            time=str(arr[i][3])
            arr3=time.split(':')
            if( float(systime[0]) == float(arr3[0])): 
                if( float(systime[1]) >= float(arr3[1])):
                    print("next bus"+arr[i][3])
                    flag=1
    if(flag==0):
        print("No bus today")
