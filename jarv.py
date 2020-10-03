import os
import pyttsx3 as pk
engine =pk.init()
engine.setProperty("rate",200)
pk.speak("Welcome to Voice Module")
pk.speak("Hope you are fine in this Crisis")
engine.runAndWait()
pk.speak("Let's Begin")
while True:   
    pk.speak("What Program would you like to open?")
    p = input()
    if("run" in p) and (("browser" in p) or ("chrome" in p)):
        pk.speak(print("Opening a Browser!"))
        os.system("google-chrome")
    elif("run" in p) and (("mediaplayer" in p) or ("songplayer" in p)):
        pk.speak(print("Opening Media Player!"))
        os.system("vlc")
    elif("run" in p) and (("notepad" in p)or("editor" in p)):
        print("Opening Text Editor! ")
        os.system("gedit file")
    elif("Calender" in p):
        print("Opening Calender")
        os.system("calc")    
    elif("run" in p) and (("jupyter" in p)or("IDE" in p)):
        print("Opening Jupyter IDE")
        os.system("jupyter notebook")
    elif("run" in p) and("kubernetes" in p):
        print("Opening the Kubernetes Cluster in VM....Might Take some time.....")      
        os.system("minikube.exe start") 
    elif(("show" in p)or("listout" in p))and("directory" in p):  
        print("We are Listing all the directories...")
        os.system("ls")  
    elif("clear" in p)and("screen" in p):
        os.system("clear")     
                      
    elif("exit" in p):
        print("We are closing the program!")
        os.system(exit())
    break
