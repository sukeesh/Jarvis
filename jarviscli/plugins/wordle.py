import requests
from plugin import plugin, require



@plugin('wordle')
def wordle(jarvis, s):
    initialText = "Welcome to Wordle!\n" \
                  "You have 6 attempts to guess the 5 letter word\n" \
                  "If a letter you guess is in the word, it will appear in lowercase\n" \
                  "If a letter you guess is in the word and at the correct position, it will appear in uppercase\n" \
                  "Good luck and have fun!\n"
    print(initialText)
    
    WORLDLE_API = "https://wordle-api.vercel.app/api/wordle"
    attempts = 6

    while attempts>0:
        guess = input("Enter Your Guess : ")
        myobj = {'guess': guess}

        x = requests.post(WORLDLE_API, json = myobj)


        if x.status_code == 404:
            jarvis.say("Invalid guess")
            return
        x.raise_for_status()

        results = x.json()
        if results['was_correct']:
            jarvis.say("You guessed correctly, congrats!")
            return
        
        output = ""
        for char in results['character_info']:
            if char['scoring']['in_word']:
                if char['scoring']['correct_idx']:
                    output = output + (char['char'].upper())
                else:
                    output= output +char['char']
            else:
                output = output +"_"
        print(output)



        attempts-=1
    jarvis.say("Oh no you lost, go here for the answer: https://wordle-api.vercel.app/")

