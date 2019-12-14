from plugin import plugin, require, LINUX
from colorama import Fore
import Jarvis


speech_installed = True
try:
    import speech_recognition as sr  
    import playsound
    import gtts
    #from gtts import gTTS 
    import os
    import wolframalpha
    from selenium import webdriver
    pass
except ImportError:
    print("import error")
    speech_installed = False

if speech_installed:
    requirements = []
else:
    requirements = [
        'speech_installed (install speech_recognition playsound + re-run setup.sh)']


#global values
num = 1


@require(native=requirements, platform=LINUX)
@plugin("open speech")
def open_speech__LINUX(jarvis, s):
    """Jarvis will open the gui for you."""
    jarvis.say("Opening speech.......",Fore.RED)

    assistant_speaks("What's your name, Human?")
    name ='Human'
    name = get_audio()
    assistant_speaks("Hello, " + str(name) + '.')

    while(1):
        assistant_speaks("What can i do for you?")
        text = str(get_audio()).lower()
        if text == 0:
            continue

        if "exit" in str(text) or "bye" in str(text) or "sleep" in str(text):
            assistant_speaks("Ok bye, "+ str(name)+'.')
            break

        # calling process text to process the query
        process_text(text)





# sub functions
def assistant_speaks(output): 
    global num 
  
    # num to rename every audio file  
    # with different name to remove ambiguity 
    num += 1
    print("PerSon : ", output) 
  
    toSpeak = gtts.gTTS(text = output, lang ='en', slow = False) 
    # saving the audio file given by google text to speech 
    file = str(num)+".mp3"
    toSpeak.save(file) 
      
    # playsound package is used to play the same file. 
    playsound.playsound(file, True)  
    os.remove(file) 



  
def get_audio(): 
  
    rObject = sr.Recognizer() 
    audio = '' 
  
    with sr.Microphone() as source: 
        print("Speak...") 
          
        # recording the audio using speech recognition 
        audio = rObject.listen(source, phrase_time_limit = 5)  
    print("Stop.") # limit 5 secs 
  
    try: 
  
        text = rObject.recognize_google(audio, language ='en-US') 
        print("You : ", text) 
        return text 
  
    except: 
  
        assistant_speaks("Could not understand your audio, PLease try again !") 
        return 0



def process_text(input): 
    try: 
        if 'search' in input or 'play' in input: 
            # a basic web crawler using selenium 
            search_web(input) 
            return
  
        elif "who are you" in input or "define yourself" in input: 
            speak = '''Hello, I am Jarvis. Your personal Assistant. 
            I am here to make your life easier. You can command me to perform 
            various tasks such as calculating sums or opening applications'''
            assistant_speaks(speak) 
            return
  
        elif "who made you" in input or "created you" in input: 
            speak = "I have been created by Human."
            assistant_speaks(speak) 
            return
  
        elif "geeksforgeeks" in input:# just 
            speak = """Geeks for Geeks is the Best Online Coding Platform for learning."""
            assistant_speaks(speak) 
            return
  
        elif "calculate" in input.lower(): 
              
            # write your wolframalpha app_id here 
            app_id = "WOLFRAMALPHA_APP_ID" 
            client = wolframalpha.Client(app_id) 
  
            indx = input.lower().split().index('calculate') 
            query = input.split()[indx + 1:] 
            res = client.query(' '.join(query)) 
            answer = next(res.results).text 
            assistant_speaks("The answer is " + answer) 
            return
  
        elif 'open' in input: 
              
            # another function to open  
            # different application availaible 
            open_application(input.lower())  
            return
  
        else: 
  
            assistant_speaks("I can search the web for you, Do you want to continue?") 
            ans = get_audio() 
            if 'yes' in str(ans) or 'yeah' in str(ans): 
                search_web(input) 
            else: 
                return
    except : 
  
        assistant_speaks("I don't understand, I can search the web for you, Do you want to continue?") 
        ans = get_audio() 
        if 'yes' in str(ans) or 'yeah' in str(ans): 
            search_web(input) 

def search_web(input): 
  
    driver = webdriver.Firefox() 
    driver.implicitly_wait(1) 
    driver.maximize_window() 
  
    if 'youtube' in input.lower(): 
  
        assistant_speaks("Opening in youtube") 
        indx = input.lower().split().index('youtube') 
        query = input.split()[indx + 1:] 
        driver.get("http://www.youtube.com/results?search_query =" + '+'.join(query)) 
        return
  
    elif 'wikipedia' in input.lower(): 
  
        assistant_speaks("Opening Wikipedia") 
        indx = input.lower().split().index('wikipedia') 
        query = input.split()[indx + 1:] 
        driver.get("https://en.wikipedia.org/wiki/" + '_'.join(query)) 
        return
  
    else: 
  
        if 'google' in input: 
  
            indx = input.lower().split().index('google') 
            query = input.split()[indx + 1:] 
            driver.get("https://www.google.com/search?q =" + '+'.join(query)) 
  
        elif 'search' in input: 
  
            indx = input.lower().split().index('google') 
            query = input.split()[indx + 1:] 
            driver.get("https://www.google.com/search?q =" + '+'.join(query)) 
  
        else: 
  
            driver.get("https://www.google.com/search?q =" + '+'.join(input.split())) 
  
        return


# function used to open application 
# present inside the system. 
def open_application(input): 
  
    if "chrome" in input: 
        assistant_speaks("Google Chrome") 
        os.startfile('C:\Program Files (x86)\Google\Chrome\Application\chrome.exe') 
        return
  
    elif "firefox" in input or "mozilla" in input: 
        assistant_speaks("Opening Mozilla Firefox")
        # for linux
        os.system("firefox")
        # for windows
        #os.startfile('C:\Program Files\Mozilla Firefox\\firefox.exe') 
        return
  
    elif "clock" in input: 
        assistant_speaks("Opening X clock") 
        # for linux
        os.system("firefox")
        # for windows
        #os.startfile('C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office 2013\\Word 2013.lnk') 
        return
  
    elif "office" in input: 
        assistant_speaks("Opening Libre Office") 
        os.system("libreoffice")
        #os.startfile('C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Microsoft Office 2013\\Excel 2013.lnk') 
        return

    elif "camera" in input: 
        assistant_speaks("Opening Ubuntu Cheese") 
        os.system("cheese")

        return
  
    else: 
  
        assistant_speaks("Application not available") 
        return

