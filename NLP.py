import speech_recognition as sr
import pyttsx3

# initialize recognizer
r = sr.Recognizer()

while(True):
    try:
        with sr.Microphone() as source:
            # wait to let recognizer adjust
            r.adjust_for_ambient_noise(source, duration=0.1)

            # listen to user
            audio = r.listen(source)

            # transcribe audio
            text = r.recognize_google(audio)
            text = text.lower()

            print(text)

            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
    except:
        continue