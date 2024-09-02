from colorama import Fore
from plugin import plugin


@plugin("caesar cipher")
def caesar_cipher_converter(jarvis, s):
    """Main function that handles the Caesar cipher plugin."""
    option = get_option(jarvis)
    if option == 1:
        plain_to_cipher(jarvis)
    elif option == 2:
        cipher_to_plain(jarvis)


def get_option(jarvis):
    """
    Presents options to the user and returns their choice.

    Args:
        jarvis: The Jarvis assistant instance.

    Returns:
        option (int or None): 1 for plain-to-cipher, 2 for cipher-to-plain,
                              None for exit.
    """
    jarvis.say("~> What can I do for you?", Fore.RED)
    print("1: Convert plain text to cipher")
    print("2: Convert cipher to plain text")
    print("3: Exit")
    print()

    while True:
        try:
            # Get user input and convert it to an integer
            option = int(jarvis.input("Enter your choice: ", Fore.GREEN))
            if option == 3:
                return None  # Exit option
            elif option in [1, 2]:
                return option  # Valid options
            else:
                jarvis.say("Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        except ValueError:
            # Handle cases where the input isn't a valid integer
            jarvis.say("Invalid input! Enter a number from the choices provided.", Fore.YELLOW)
        print()


def caesar_cipher(text, shift):
    """
    Converts the text using a Caesar cipher with the specified shift.

    Args:
        text (str): The input string to be converted.
        shift (int): The number of positions to shift each letter.

    Returns:
        converted (str): The resulting converted string.
    """
    converted = ""
    for char in text:
        if char.isalpha():
            # Determine starting ASCII code (A/a) based on case
            start = ord('A') if char.isupper() else ord('a')
            # Perform the shift within the bounds of the alphabet
            converted += chr((ord(char) - start + shift) % 26 + start)
        else:
            converted += char  # Non-alphabetic characters are not shifted
    return converted


def plain_to_cipher(jarvis):
    """
    Converts plain text to Caesar cipher text with a shift of 3.

    Args:
        jarvis: The Jarvis assistant instance.
    """
    user_input = get_user_input(jarvis)
    converted = caesar_cipher(user_input, 3)
    jarvis.say(converted, Fore.YELLOW)


def cipher_to_plain(jarvis):
    """
    Converts Caesar cipher text back to plain text with a shift of -3.

    Args:
        jarvis: The Jarvis assistant instance.
    """
    user_input = get_user_input(jarvis)
    converted = caesar_cipher(user_input, -3)
    jarvis.say(converted, Fore.YELLOW)


def get_user_input(jarvis):
    """
    Prompts the user to enter a string for conversion.

    Args:
        jarvis: The Jarvis assistant instance.

    Returns:
        user_input (str): The string entered by the user.
    """
    while True:
        user_input = jarvis.input("Enter string to convert: ")
        if len(user_input) > 0:
            return user_input  # Return the input if it's non-empty
        else:
            jarvis.say("String length should be minimum 1.", Fore.YELLOW)
