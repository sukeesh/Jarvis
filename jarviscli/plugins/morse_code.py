from plugin import plugin


@plugin("morsecode")
class morsecode:
    """
    morsecode is a morse code translator
    supports letters A-Z,a-z , numbers 0-9
    and "," "." "?" "/" "-" "(" ")"
    morse doesn't have a distinction between
    lower case and upper case characters
    so the program uses upper case characters for decoding
    when decoding use:
    "." for dot
    "-" for dash
    Letters are separated by spaces and words by "|"
    for instance .... . .-.. .-.. --- | -.-- --- ..-
    is hello you
    First you choose if you want to encode or decode a text.
    Second you enter the text.
    The program then shows the altered text.
    """
    morse_code = {
        'A': '.-', 'B': '-...',
        'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....',
        'I': '..', 'J': '.---', 'K': '-.-',
        'L': '.-..', 'M': '--', 'N': '-.',
        'O': '---', 'P': '.--.', 'Q': '--.-',
        'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--',
        'X': '-..-', 'Y': '-.--', 'Z': '--..',
        '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....',
        '7': '--...', '8': '---..', '9': '----.',
        '0': '-----', ',': '--..--', '.': '.-.-.-',
        '?': '..--..', '/': '-..-.', '-': '-....-',
        '(': '-.--.', ')': '-.--.-'
    }
    encoded_char = [
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
        "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
        "U", "V", "W", "X", "Y", "Z", "1", "2", "3", "4",
        "5", "6", "7", "8", "9", "0", ",", ".", "?", "/",
        "-", "(", ")", " "
    ]
    decoded_char = [
        ".", "-", "|", " "
    ]

    def __call__(self, jarvis, s):

        jarvis.say("The supported characters are:")
        jarvis.say("letters A-Z,a-z")
        jarvis.say("numbers 0-9")
        jarvis.say("\",\" \".\" \"?\" \"/\" \"-\" \"(\" \")\"")
        jarvis.say("morse doesn't have a distinction between")
        jarvis.say("lower case and upper case characters")
        jarvis.say("so the program uses upper case characters for decoding")
        jarvis.say("when decoding use:")
        jarvis.say("\".\" for dot")
        jarvis.say("\"-\" for dash")
        jarvis.say("Letters are separated by spaces and words by \"|\"")
        jarvis.say("for instance .... . .-.. .-.. --- | -.-- --- ..-")
        jarvis.say("is hello you")
        jarvis.say("choose what to do with the numbers:")
        jarvis.say("1. encoding")
        jarvis.say("2. decoding")
        flag = True
        while flag:
            choice = jarvis.input_number("input your choice: ")
            if choice == 1:
                message = self.encoder_input(jarvis, "input to encoder: ")
                jarvis.say(self.encoder(message))
                flag = False
            elif choice == 2:
                message = self.decoder_input(jarvis, "input to decoder: ")
                jarvis.say(self.decoder(message))
                flag = False
            else:
                jarvis.say("Not a valid input. Try again")

    def encoder(self, text):
        encoded = ""
        capitalstext = text.upper()
        for letter in capitalstext:
            if letter != " ":
                # Changes the character with it's morse code equivalent
                encoded = encoded + self.morse_code[letter] + " "
            else:
                encoded = encoded + "| "

        return encoded

    def encoder_input(self, jarvis, text):

        while True:
            correct = True
            check_input = jarvis.input(text)
            for letter in check_input.upper():
                if not(letter in self.encoded_char):
                    correct = False
                    break

            if(correct):
                return check_input

            text = "Not a valid input. Try again: "

    def decoder(self, text):
        text += " "
        decoded = ""
        current = ""
        # if there is a space then it is either
        # the end of a word or the end of a letter
        for letter in text:

            if letter != " ":
                current += letter

            else:
                if current == "|":
                    decoded = decoded + " "
                else:

                    try:
                        # accessing the keys using their values
                        decoded += list(self.morse_code.keys()
                                        )[list(self.morse_code.values()
                                               ).index(current)]
                    except BaseException:
                        decoded = "This is a false morse code"
                        return decoded

                current = ''

        return decoded

    def decoder_input(self, jarvis, text):

        while True:
            correct = True
            check_input = jarvis.input(text)
            for letter in check_input:
                if not(letter in self.decoded_char):
                    correct = False
                    break
            if(correct):
                return check_input

            text = "Not a valid unit. Try again: "
