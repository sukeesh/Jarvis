from colorama import Fore

def wordIndex(data, word):
    wordList = data.split()
    return wordList.index(word)

def print_say(text, self, color=""):
	if self.enable_voice:
		self.speech.text_to_speech(text)
	print(color + text + Fore.RESET)
