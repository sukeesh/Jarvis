from colorama import Fore

from plugin import plugin


@plugin("caesar cipher")
def caesar_cipher_converter(jarvis, str):
    option = get_option(jarvis)
    if option == 1:
        plain_to_cipher(jarvis)
    elif option == 2:
        cipher_to_plain(jarvis)
    else:
        return


def get_option(jarvis):
    jarvis.say("~> What can I do for you?", Fore.RED)
    print("1: Convert plain text to cipher")
    print("2: Convert cipher to plain text")
    print("3: Exit")
    print()

    while True:
        try:
            option = int(jarvis.input("Enter your choice: ", Fore.GREEN))
            if option == 3:
                return
            elif option == 1 or option == 2:
                return option
            else:
                jarvis.say(
                    "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        except ValueError:
            jarvis.say(
                "Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        print()


def plain_to_cipher(jarvis):
    user_input = get_user_input(jarvis)
    converted = ""

    for i in user_input:
        if is_ascii(i):
            if i.isalpha():
                if i.isupper():
                    converted += chr((ord(i) - 68) % 26 + 65)
                else:
                    converted += chr((ord(i) - 100) % 26 + 97)
            else:
                converted += i
        else:
            x = ord(i)
            if x >= 192 and x <= 255:
                converted += chr((ord(i) - 195) % 63 + 192)
            else:
                converted += i

    jarvis.say(converted, Fore.YELLOW)


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def cipher_to_plain(jarvis):
    user_input = get_user_input(jarvis)
    converted = ""

    for i in user_input:
        if is_ascii(i):
            if i.isalpha():
                if i.isupper():
                    converted += chr((ord(i) - 62) % 26 + 65)
                else:
                    converted += chr((ord(i) - 94) % 26 + 97)
            else:
                converted += i
        else:
            x = ord(i)
            if x >= 192 and x <= 255:
                converted += chr((ord(i) - 189) % 63 + 192)
            else:
                converted += i

    jarvis.say(converted, Fore.YELLOW)


def get_user_input(jarvis):
    while True:
        try:
            user_input = jarvis.input("Enter string to convert: ")
            if len(user_input) > 0:
                return user_input
            else:
                jarvis.say(
                    "String length should be minimum 1.", Fore.YELLOW)
        except ValueError:
            jarvis.say("Sorry, I didn't understand that.", Fore.RED)
            continue

    return
