import time
import sys
import requests
import json
import re
import curses
from plugin import plugin, require, UNIX
import os
import csv
from colorama import Fore

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


class GameState (object):
    RUNNING = 1
    ENDED = 2


default_text_color = Fore.WHITE
incorrect_color = Fore.RED
correct_color = Fore.GREEN
n_words = 4

total_time = 100

info = {}


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""

    def __init__(self):
        self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


class _GetchUnix:
    def __call__(self):
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


getch = _Getch()


class Letter():
    class State(object):

        def __init__(self):
            pass

        CORRECT = 1
        INCORRECT = 2
        UNENTERED = 3

    def __init__(self):
        pass

    def setLetter(self, letter):
        self.letter = letter
        self.state = Letter.State.UNENTERED

    def __str__(self):
        string = ''
        if self.state == Letter.State.UNENTERED:
            string += default_text_color
        elif self.state == Letter.State.CORRECT:
            string += correct_color
        elif self.state == Letter.State.INCORRECT:
            string += incorrect_color
        string += self.letter
        return string


def get_text():
    response = requests.get('http://www.randomtext.me/api/\
        gibberish/p-5/' + str(n_words))
    json_data = json.loads(response.content)
    random_text = json_data['text_out']
    clean_text = random_text
    clean_text = re.sub(re.compile('<.*?>'), '', random_text)
    clean_text = clean_text.replace('\r', '').replace('\\r', '')
    clean_text = clean_text.replace('.', '. ')
    return clean_text


def format_time(seconds):
    new_minutes = int(seconds / 60)
    new_seconds = int(seconds - new_minutes * 60)

    new_minutes = str(new_minutes)
    new_seconds = str(new_seconds)

    new_minutes = '0' * (2 - len(new_minutes)) + new_minutes
    new_seconds = '0' * (2 - len(new_seconds)) + new_seconds

    return new_minutes + ':' + new_seconds


def take_input():
    entered_letter = getch()
    if (entered_letter == '='):
        game_end()
    letter_object = info['letters'][info['position']]
    print(letter_object.letter)
    if (entered_letter == letter_object.letter):
        letter_object.state = Letter.State.CORRECT
        info['score'] += 1
        if(entered_letter == ' '):
            if(not info['mistake_in_current_word']):
                info['words'] += 1
            info['mistake_in_current_word'] = False
    else:
        letter_object.state = Letter.State.INCORRECT
        info['mistake_in_current_word'] = True
    info['position'] += 1


def reset():
    info['state'] = GameState.RUNNING
    info['text'] = get_text()
    info['words'] = 0
    info['time_left'] = total_time
    info['letters'] = ['-1'] * len(info['text'])
    info['score'] = 0
    info['position'] = 0
    info['mistake_in_current_word'] = False


def game_start():
    reset()
    for i in range(len(info['text'])):
        print(info['text'][i])
        info['letters'][i] = Letter()
        info['letters'][i].setLetter(info['text'][i])

    game_running()


def game_running():
    while(info['state'] == GameState.RUNNING):
        time_0 = time.time()

        print_screen()
        take_input()

        time_1 = time.time()
        info['time_left'] -= (time_1 - time_0)
        if(info['time_left'] <= 0 or info['position'] == len(info['text'])):
            game_end()


def game_end():
    info['state'] = GameState.ENDED
    time_diff = (total_time - info['time_left']) / 60
    if time_diff > 0:
        wpm = info['words'] / ((total_time - info['time_left']) / 60)
    else:
        wpm = 0

    print(default_text_color + '\n\nWords per minute - {}'.format(wpm))
    if wpm >= 20:
        with open(os.path.join(FILE_PATH, "../data/typing_test_data.csv"),
                  mode='r') as f:
            data = list(csv.reader(f))
            for i in range(len(data)):
                if int(data[i][0]) > int(wpm) and i != 0:
                    print('You are better than {}% of people!'
                          .format(float(data[i - 1][1]) * 100))
                    break


def print_screen():
    print("\033c")
    string = 'Welcome to the typing text game. Enter the letters shown \
        below (\'=\' to quit) - \n'
    string += '\nScore - {}\t Time - {}\t Words -  \
        {}\n\n'.format(info['score'], format_time(info['time_left']),
                       info['words'])
    for i in range(len(info['letters'])):
        string += str(info['letters'][i])
    sys.stdout.write(string)


@require(network=True, platform=UNIX)
@plugin("typingtest")
def typingtest(jarvis, s):
    game_start()
