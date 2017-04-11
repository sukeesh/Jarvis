from colorama import Fore

def wordIndex(data, word):
    wordList = data.split()
    return wordList.index(word)

def print_say(text, self, color=""):
	"""
        This method give the jarvis the ability to print a text
	and talk when sound is enable.
        :param text: the text to print (or talk)
               color: Fore.COLOR (ex Fore.BLUE), color for text
        :return: Nothing to return.
        """
	if self.enable_voice:
		self.speech.text_to_speech(text)
	print(color + text + Fore.RESET)
