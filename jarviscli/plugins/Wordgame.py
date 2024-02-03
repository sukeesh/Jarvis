import requests
from wonderwords import RandomWord
import time
import enchant



def generateWord(letter):
    r = RandomWord()
    new_word=r.word(starts_with=letter)
    return new_word


d = enchant.Dict("en_US")

continue_playing='Y'
while continue_playing=='Y' or continue_playing=='y':
    max_seconds_to_answer=int(input("Give how many seconds you would like to have to find your answers \n"))
    rounds=int(input("Give the number of rounds after which you will win the game \n"))
    current_rounds=1
    Continue=True
    word=input("Give a word \n")

    while current_rounds<=rounds:
        print("Round ",current_rounds)
        jarvis_answer=generateWord(word[len(word)-1])
        print("Jarvis' answer is: ",jarvis_answer)

        start_time=time.time()
        word=input("Give a word starting with the letter: \""+str(jarvis_answer[len(jarvis_answer)-1])+"\" , You have "+str(max_seconds_to_answer)+" seconds to answer! \n")
        end_time=time.time()
        time_to_answer=end_time-start_time
        #print(time_to_answer)
        current_rounds+=1

        if time_to_answer>max_seconds_to_answer:
            print("You were too late to answer! You lost. ")
            break

        if word[0]!=jarvis_answer[len(jarvis_answer)-1]:
            #print("Your word does not start with the last letter of jarvis' word! You lost. ")
            print("Wrong answer! You lost. ")
            break
            
        if (not d.check(word)) or len(word)<2:
            print("Wrong word! You lost. ")
            break 

    if current_rounds>rounds:
        print("Congratulations! You won all "+str(rounds)+" rounds against jarvis!")

    continue_playing=input("If you want to continue playing press Y/y, otherwise press N/n \n")