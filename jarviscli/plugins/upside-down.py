from plugin import plugin
from colorama import Fore


@plugin('upside down')
def generate_random_list(jarvis, str):
    user_input = jarvis.input("Enter string to be converted to upside-down (only english letters will be converted): ")
    result = convert_input(jarvis, user_input)
    jarvis.say(result, Fore.GREEN)


def convert_input(jarvis, u_input):
    upside_str = 'zʎxʍʌnʇsɹbdouɯןʞſıɥbɟǝpɔqɐ'
    normal_str = 'abcdefghijklmnopqrstuvwxyz'
    upside_str = upside_str[::-1]
    converter_dict = {a: b for a, b in zip(normal_str, upside_str)}
    result = ''
    for letter in u_input:
        if letter in converter_dict:
            result += converter_dict[letter]
    return result[::-1]
