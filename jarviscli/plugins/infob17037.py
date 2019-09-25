from plugin import plugin
import subprocess


@plugin("infob17037")
def infob17037(jarvis, s):
    """Repeats what you type"""
    stri0 = "Welcome to the info plugin of ATYANT YADAV roll num B17037."
    stri1 = "Please select one of the options below:"
    stri2 = "->[F]ull name 				 prints your full name "
    stri3 = "->[H]ometown 				 prints your hometown "
    stri4 = "->Favourite [M]ovie 			 prints your fav movie "
    stri5 = "->Favourite [S]portsperson	 	 prints your fav sportsperson "
    stri6 = "->Launch [P]ython program written by me  launch a (short) python program"
    stri7 = "->[Q] to quit"
    jarvis.say(stri0)
    jarvis.say(stri1)
    jarvis.say(stri2)
    jarvis.say(stri3)
    jarvis.say(stri4)
    jarvis.say(stri5)
    jarvis.say(stri6)
    jarvis.say(stri7)
    
    flagg = 1

    while flagg and 1:
        che = input()
        if(che=="Q"):
            flagg=0
        if(che=="F"):
            jarvis.say("ATYANT YADAV")
        elif(che=="H"):
            jarvis.say("KALAKHARI")
        elif(che=="M"):
            jarvis.say("INTERESTELLER")
        elif(che=="S"):
            jarvis.say("LEBRON JAMES")
        elif(che=="Q"):
            jarvis.say("Exiting....")
        elif(che=="P"):
            jarvis.say("GIve me full path of program to run:")
            paa = input()
            cmd1 = ["python3", paa]
            process1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
            for line in process1.stdout:
                print(line)
        else:
            jarvis.say("INCORRECT OPTION, TRY AGAIN....")

    