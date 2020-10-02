# from plugin import plugin
from colorama import Fore
from random import choice

board = {"1": "   ", "2": "   ", "3": "   ",
         "4": "   ", "5": "   ", "6": "   ",
         "7": "   ", "8": "   ", "9": "   "}

board_keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
# An array of keys of the board to reset him by a function.

cases_victory = [[1, 2, 3], [4, 5, 6], [7, 8, 9], 
                 [1, 4, 7], [2, 5, 8], [3, 6, 9], 
                 [1, 5, 9], [3, 5, 7]]
# It's used by the Judge to verify a win, and
# by Jarvis to see possible wins

@plugin("tic_tac_toe")

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

def game_mode():
    text = ""
    text += "=> Select An Option:\n"
    text += "[local] => For two players.\n"
    text += "[exit] => Exit TicTacToe"
    print(text)
    
    mode = input("[mode] > ")
    if mode == "local":
        local_game()
    elif mode == "exit":
        exit()
    else:
        print("[error] please select an valid option.")
        game_mode()


def local_game():
    # This method will manage the game (local).
    restart_board()
    players = choice([["X", "O"], ["O", "X"]])
    player_1, player_2 = players[0], players[1]
    intro = "> The first will be...\n"
    intro += f"> {player_1}!\n"
    intro += "> Good luck players!"
    print(intro)
    while True:
        turn(player_1) # First Player
        turn(player_2) # Second Player


def turn(which_player):
    # Will do all the steps that build a "turn"
    place = str(choosing_path(which_player)) 
    # <= Ask to the player to do a play 
    do_a_move(which_player, place)
    # <= Exec the player move
    verdict = judge(which_player)
    # <= Save the verdict from the Judge
    is_game_end(which_player, verdict)

def is_game_end(which_player, verdict):
    if verdict == "void":
        pass # No one win.
    elif verdict == "win":
        # If the player win
        show_board()
        print(f"> Player {which_player} won!")
        game_mode()
    elif verdict == "tie":
        # If we have a Tie.
        show_board()
        print("> A tie! Good Game Players!")
        game_mode()


def choosing_path(which_player):
    show_board()
    try:
        move = int(input(f"[{which_player} turn!] Select a Place! > "))
    except ValueError:
        print("> Please type a number! ")
        choosing_path(which_player)

    if validate_play(move) is False:
        print("Please choose an Empty House!")
        choosing_path(which_player)

    return move   

def judge(which_player):
    player_win = verify_win(which_player)
    tie = verify_tie()
    if player_win is True:
        return "win"
    if tie is True:
        return "tie"
    
    return "void"

def verify_win(which_player):
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


if __name__ == "__main__":
    game_mode()
