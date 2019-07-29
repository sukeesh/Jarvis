from plugin import plugin
import random


@plugin("random number")
def generate_random_number(jarvis, numbers):

    if numbers != "":
        input_numbers = numbers.split(' ', 1)

        try:
            smallest_number = int(input_numbers[0])
            higher_number = int(input_numbers[1])
        except (ValueError, IndexError):
            print('Values are invalid please:')
            smallest_number, higher_number = get_user_input(jarvis)
    else:
        smallest_number, higher_number = get_user_input(jarvis)

    """If the user change the order of input"""
    if higher_number < smallest_number:
        aux = higher_number
        higher_number = smallest_number
        smallest_number = aux

    pre_text = 'Your random number in range [%d, %d] is' \
               % (smallest_number, higher_number)
    rand_number = random.randint(smallest_number, higher_number)
    print(pre_text, rand_number)


def get_user_input(jarvis):
    string_fail = True
    while string_fail:
        try:
            smallest_number = int(jarvis.input('Enter the smallest number: '))
            string_fail = False
        except ValueError:
            print('Only integers will be accepted')

    string_fail = True

    while string_fail:
        try:
            higher_number = int(jarvis.input('Enter the higher number: '))
            string_fail = False
        except ValueError:
            print('Only integers will be accepted')

    return smallest_number, higher_number
