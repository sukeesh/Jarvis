import requests
from wonderwords import RandomWord
import time
import enchant
from plugin import plugin, complete, require
from colorama import Fore


    
def generateWord(letter):
    r = RandomWord()
    new_word=r.word(starts_with=letter)
    return new_word

@plugin("word_game")
def word_game(jarvis,s):
    d = enchant.Dict("en_US")

    continue_playing='Y'
    while continue_playing=='Y' or continue_playing=='y':
        max_seconds_to_answer=int(jarvis.input("Give how many seconds you would like to have to find your answers \n",color=Fore.GREEN))
        rounds=int(jarvis.input("Give the number of rounds after which you will win the game \n",color=Fore.GREEN))
        current_rounds=1
        
        while True:
            word=jarvis.input("Give a word: \n",color=Fore.GREEN)
            if not ((not d.check(word)) or len(word)<2):
                break
            else:
                jarvis.say("Give a proper word!",color=Fore.RED)

        while current_rounds<=rounds:
            jarvis.say("Round "+str(current_rounds),color=Fore.YELLOW)
            jarvis_answer=generateWord(word[len(word)-1])
            jarvis.say("Jarvis' answer is: "+jarvis_answer,color=Fore.YELLOW)

            start_time=time.time()
            word=jarvis.input("Give a word starting with the letter: \""+str(jarvis_answer[len(jarvis_answer)-1])+"\" , You have "+str(max_seconds_to_answer)+" seconds to answer! \n",color=Fore.GREEN)
            end_time=time.time()
            time_to_answer=end_time-start_time
            current_rounds+=1

            if time_to_answer>max_seconds_to_answer:
                jarvis.say("You were too late to answer! You lost. ",color=Fore.RED)
                break

            if word[0]!=jarvis_answer[len(jarvis_answer)-1]:
                jarvis.say("Your word does not start with the last letter of jarvis' word! You lost. ",color=Fore.RED)
                break
                
            if (not d.check(word)) or len(word)<2:
                jarvis.say("Wrong word! You lost. ",color=Fore.RED)
                break 

        if current_rounds>rounds:
            jarvis.say("Congratulations! You won all "+str(rounds)+" rounds against jarvis!",color=Fore.YELLOW)

        continue_playing=jarvis.input("If you want to continue playing press Y/y, otherwise press N/n \n")
        
