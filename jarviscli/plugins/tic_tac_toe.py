from plugin import plugin
from colorama import Fore

board = {'7': '   ', '8': '   ', '9': '   ',
         '4': '   ', '5': '   ', '6': '   ',
         '1': '   ', '2': '   ', '3': '   '}

board_keys = []

for key in board:
    board_keys.append(key)


def restartBoard(board):
    for key in board_keys:
        board[key] = '   '


def printBoard(board):
    print(board['7'] + '|' + board['8'] + '|' + board['9'])
    print('-----------')
    print(board['4'] + '|' + board['5'] + '|' + board['6'])
    print('-----------')
    print(board['1'] + '|' + board['2'] + '|' + board['3'])


def checkWinner(board, jarvis, turn):
    if board['7'] == board['8'] == board['9'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    elif board['4'] == board['5'] == board['6'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    elif board['1'] == board['2'] == board['3'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    elif board['1'] == board['4'] == board['7'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    elif board['2'] == board['5'] == board['8'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    elif board['3'] == board['6'] == board['9'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    elif board['7'] == board['5'] == board['3'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    elif board['1'] == board['5'] == board['9'] != '   ':
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    else:
        return False


@plugin("tic_tac_toe")
def game(jarvis, s):
    """
    The tic tac toe game for two players
    Positions on the board are placed as follow
     7 | 8 | 9
    -----------
     4 | 5 | 6
    -----------
     1 | 2 | 3
    """

    restartBoard(board)
    turn = ' X '
    count = 0

    while count < 10:
        printBoard(board)
        s = jarvis.input(turn + "turn. " + "Choose a position!", Fore.BLUE)
        if s not in board_keys:
            jarvis.say(
                "Incorrect input. Please print any number from 1 to 9 corresponding to the position on the board!", Fore.RED)
            continue

        if board[s] == '   ':
            board[s] = turn
            count += 1
        else:
            jarvis.say(
                "This position is already filled.\nChoose another position!", Fore.RED)
            continue

        if count >= 5:
            if(checkWinner(board, jarvis, turn)):
                break

        # Check if a draw
        if count == 9:
            printBoard(board)
            jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
            jarvis.say("It's a Draw!", Fore.GREEN)
            break

        # Change the turn
        if turn == ' X ':
            turn = ' O '
        else:
            turn = ' X '


if __name__ == "__main__":
    game()
