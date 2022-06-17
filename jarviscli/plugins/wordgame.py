from plugin import plugin
import random
from tkinter import *
from tkinter import messagebox 

@plugin("wordgame")
with open("./Jarvis/jarviscli/data/wordgame_word_list.txt", "r") as wordslist:
    data = wordslist.read()
    words = data.split()
    word_pos = random.randint(0, len(words) - 1)
    random_word = words[word_pos]

root = Tk()

GREEN = "#039108"
YELLOW = "#fcba03"
BLACK = "#000000"
GRAY = "#828282"
WHITE = "#ffffff"

root.title('Word Game')
root.geometry('300x400')
root.resizable(False, False)
root.config(bg = BLACK)

number_of_guesses = 0
maximum_trial = 5

word_input = Entry(root)
word_input.grid(row = 9, column = 0, padx = 10, pady = 10, columnspan = 5)
word_guessed = []

characters_left = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                   'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                   'w', 'x', 'y', 'z']


def get_guess():

    global random_word
    global number_of_guesses
    global word_guessed
    global characters_left
    
    guess = word_input.get()
    guess = guess.lower()

    if number_of_guesses <= maximum_trial:
    
        if guess not in word_guessed:
        
            if len(guess) == 5 and guess in data:
            
                if random_word == guess:
                
                    for i, character in enumerate(guess):
                    
                        label = Label(root, text = character.upper(),
                                      font = "Arial 16")
                        label.grid(row = number_of_guesses,
                                   column = i, padx = 10, pady = 10)
                                   
                        if character == random_word[i]:
                            label.config(bg = GREEN, fg = WHITE)
                            
                    messagebox.showinfo("Correct!",
                                        f"Correct! The word was {random_word.title()}")
                                        
                    number_of_guesses = 5
                    
                else:
                    for i, character in enumerate(guess):
                        label = Label(root, text = character.upper(),
                                      font = "Arial 16")
                        label.grid(row = number_of_guesses,
                                   column = i, padx = 10, pady = 10)
                                   
                        if character == random_word[i]:
                            label.config(bg = GREEN, fg = WHITE)
                            
                        if character in random_word and not character == random_word[i]:
                            label.config(bg = YELLOW, fg = WHITE)
                            
                        if character not in random_word:
                            label.config(bg = GRAY, fg = WHITE)
                            
                            if character in characters_left:
                                characters_left.remove(character)
                        
                        word_guessed.append(guess)
                        
                number_of_guesses += 1
                
            else:
                messagebox.showerror("Wordgame ERROR",
                                     "Not in word list.")
        else:
            messagebox.showerror("Wordgame ERROR",
                                 "Try a different word you did not guessed.")

    else:
        messagebox.showerror("Game over",
                             f"The word was {random_word}")
        
    word_input.delete(0, 'end')


word_guess_btn = Button(root, text = "Return", command = get_guess, bg = BLACK)
word_guess_btn.grid(row = 9, column = 6, columnspan = 2)

root.mainloop()
