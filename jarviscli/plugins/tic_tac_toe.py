from plugin import plugin
from colorama import Fore

board = {'7': '   ' , '8': '   ' , '9': '   ' ,
         '4': '   ' , '5': '   ' , '6': '   ' ,
         '1': '   ' , '2': '   ' , '3': '   ' }


def printBoard(board):
    print(board['7'] + '|' + board['8'] + '|' + board['9'])
    print('-----------')
    print(board['4'] + '|' + board['5'] + '|' + board['6'])
    print('-----------')
    print(board['1'] + '|' + board['2'] + '|' + board['3'])

def restartBoard(board):
	for key in range(1,10):
            board[str(key)] = "   "


@plugin("tic_tac_toe")
def game(jarvis, s):
	"""	the tic tac toe game for two players
	position on the board is placed as follow
	 7 | 8 | 9
	-----------
	 4 | 5 | 6
	-----------
	 1 | 2 | 3 """

	restartBoard(board)
	turn = ' X '
	count = 0

	while count < 10:
	    printBoard(board)
	    s = jarvis.input("It's your turn," + turn + ".Move to which place?", Fore.BLUE)

	    if board[s] == '   ':
	        board[s] = turn
	        count += 1
	    else:
	        jarvis.say("That place is already filled.\nMove to which place?", Fore.RED)
	        continue

	    # Check if someone won
	    if count >= 5:
	        if board['7'] == board['8'] == board['9'] != '   ': # across the top
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break
	        elif board['4'] == board['5'] == board['6'] != '   ': # across the middle
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break
	        elif board['1'] == board['2'] == board['3'] != '   ': # across the bottom
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break
	        elif board['1'] == board['4'] == board['7'] != '   ': # down the left side
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break
	        elif board['2'] == board['5'] == board['8'] != '   ': # down the middle
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break
	        elif board['3'] == board['6'] == board['9'] != '   ': # down the right side
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break
	        elif board['7'] == board['5'] == board['3'] != '   ': # diagonal
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break
	        elif board['1'] == board['5'] == board['9'] != '   ': # diagonal
	            printBoard(board)
	            jarvis.say("\nGame Over.\n", Fore.GREEN)                
	            jarvis.say(" **** " +turn + " won. ****", Fore.GREEN)                
	            break	

	    # Check if a draw
	    if count == 9:
	        printBoard(board)
	        jarvis.say("\nGame Over.\n", Fore.GREEN)                
	        jarvis.say("It's a Draw!!", Fore.GREEN)
	        break

	    #Change the turn
	    if turn ==' X ':
	        turn = ' O '
	    else:
	    	turn = ' X '


if __name__ == "__main__":
    game()
