#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
from colorama import Fore

### BASIC VARIABLES FOR TICTACTOE ###

board = {"1": "   ", "2": "   ", "3": "   ",
         "4": "   ", "5": "   ", "6": "   ",
         "7": "   ", "8": "   ", "9": "   "}

board_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

## Board Basic Functions ##

def show_board():
    horizontal_line = "-----------\n"
    printable_board = "\n"
    printable_board += board["1"] + "|" + board["2"] + "|" + board["3"] + "\n"
    printable_board += horizontal_line
    printable_board += board["4"] + "|" + board["5"] + "|" + board["6"] + "\n"
    printable_board += horizontal_line
    printable_board += board["7"] + "|" + board["8"] + "|" + board["9"] + "\n"
    print(printable_board)

def do_a_move(which_player, place): 
    board[place] = " " + which_player + " " 

def restart_board():
    for key in board_keys:
        board[key] = '   '

def end_game(which_player, message):
    show_board()
    print(message)
    game_mode()

## End Of Board Basic Functions ##

## Game Basic Functions ## 

def game_mode():
    text = ""
    text += "=> Select An Option:\n"
    text += "[local] => For two players.\n"
    # text += "[ai] => Versus Jarvis\n"
    text += "[exit] => Exit TicTacToe"
    print(text)
    
    mode = input("[mode] > ")
    if mode == "local":
        local_mode()
    # elif mode == "ai":
    #     pass  # TO-DO
    elif mode == "exit":
        exit()
    else:
        print("[error] please select an valid option.")
        game_mode()


## End Of Game Basic Functions ## 

## Player Turn ##

def player_turn(which_player):
    show_board()
    try:
        move = int(input(f"[{which_player} turn!] Select a Place! > ", Fore.BLUE))
    except ValueError:
        print("> Please type a number! ", Fore.RED)
        player_turn(which_player)

    if validate_play(move) is False:
        print("Please choose an Empty House!", Fore.RED)
        player_turn(which_player)

    return move    

## End Of Player Turn ## 

## Judge Turn ## 

def judge(which_player):
    player_win = verify_win(which_player)
    tie = verify_tie()
    if player_win is True:
        return "win"
    if tie is True:
        return "tie"
    
    return "void"

def verify_win(which_player):
    cases_victory = [[1, 2, 3], [4, 5, 6], [7, 8, 9], 
                     [1, 4, 7], [2, 5, 8], [3, 6, 9], 
                     [1, 5, 9], [3, 5, 7]]

    for line in range(0, len(cases_victory)):
        pos_0 = board[str(cases_victory[line][0])]
        pos_1 = board[str(cases_victory[line][1])]
        pos_2 = board[str(cases_victory[line][2])]
        if pos_0 == f" {which_player} " and pos_1 == f" {which_player} " and pos_2 == f" {which_player} ":
            return True
    return False

def verify_tie():
    places_with_pieces = 0
    for position in range(1, 10):
        if board[str(position)] != "   ":
            places_with_pieces += 1

    if places_with_pieces == 9:
        return True
    return False

def validate_play(play):
    if board[str(play)] == "   ":
        return True
    else:
        return False

###################

### Entire Turn ### 
def turn_manager(which_player):
    """ Will return a value of a turn """
    place = str(player_turn(which_player))
    do_a_move(which_player, place)
    verdict = judge(which_player)
    if verdict == "void":
        pass
    if verdict == "win":
        win_text = "> Player {which_player} win!"
        end_game()
        


## Game Controllers ## 
def local_mode():
    restart_board()
    players = choice([["X", "O"], ["O", "X"]])
    player_1, player_2 = players[0], players[1]
    intro = "> The first will be...\n"
    intro += f"> {player_1}!\n"
    intro += "> Good luck players!"
    print(intro, Fore.BLUE)
    
    while True:
        turn_manager(player_1)

    game_mode()


game_mode()