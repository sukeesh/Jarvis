# -*- coding: utf-8 -*-
from utilities.GeneralUtilities import print_say
from utilities.textParser import parse_number
from colorama import Fore

import random
import re


def dice(self, s):
    config = _dice_parse(s)

    error = _dice_is_error_in_config(config)
    if error:
        print_say(error, self, Fore.RED)
        return

    for roll in _dice_roll(config):
        result = "|" + "| |".join(roll) + "|"
        border = re.sub(r"\S", "-", result)

        print_say(border, self, Fore.BLUE)
        print_say(result, self, Fore.BLUE)
        print_say(border + '\n', self, Fore.BLUE)


def _dice_parse(s):
    repeat = 1
    howmany = 1
    edges = 6

    prefix = ""
    prefix_length = 0
    prefix_number = -1

    # Iterate string.
    # Search for number before keywords (edges, times, dices)
    for word_current in s.split():
        parse_result = parse_number(prefix)

        # make sure, prefix still contains only number-characters
        if parse_result[0] != prefix_length:
            # last token not part of number -> reset prefix
            prefix = word_current
            prefix_length = 1
            continue
        prefix_number = parse_result[1]

        if word_current == "edge" or word_current == "edges":
            edges = prefix_number

        if word_current == "times":
            repeat = prefix_number

        if word_current == "dices":
            howmany = prefix_number

        prefix += " "
        prefix += word_current
        prefix_length += 1

    return {"repeat": repeat, "howmany": howmany, "edges": edges}


def _dice_is_error_in_config(config):
    assert isinstance(config["edges"], int)
    assert isinstance(config["howmany"], int)
    assert isinstance(config["repeat"], int)

    if config["howmany"] == 0:
        return "No dice to roll?"
    if config["howmany"] < 0:
        return "Rolling {} dices does not really make sence ;).".format(config["howmany"])
    if config["repeat"] == 0:
        return "Roll 0 howmany? Finish!"
    if config["repeat"] < 0:
        return "Doing something {} does not really make sense ;).".format(config["repeat"])
    if config["edges"] <= 1:
        return "A dice with {} edges does not really make sense ;).".format(config["edges"])

    return False


def _dice_roll(config):
    for _ in range(config["repeat"]):
        yield [str(random.randint(1, config["edges"])) for _ in range(config["howmany"])]
