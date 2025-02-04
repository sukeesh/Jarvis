from plugin import plugin
from colorama import Fore

player, opponent = 'o', 'x'

# This function returns true if there are moves
# remaining on the board. It returns false if
# there are no moves left to play.
def isMovesLeft(board) :

	for i in range(3) :
		for j in range(3) :
			if (board[i][j] == '_') :
				return True
	return False

# This is the evaluation function as discussed
# in the article ( http://goo.gl/sJgv68 )
def evaluate(b) :

	# Checking for Rows for X or O victory.
	score = 0
	for row in range(3) :	
		if (b[row][0] == b[row][1] and b[row][1] == b[row][2]) :	
			if (b[row][0] == player) :
				score = 10
			elif (b[row][0] == opponent) :
				score = -10

	# Checking for Columns for X or O victory.
	for col in range(3) :
	
		if (score == 0 and b[0][col] == b[1][col] and b[1][col] == b[2][col]) :
		
			if (b[0][col] == player) :
				score = 10
			elif (b[0][col] == opponent) :
				score = -10

	# Checking for Diagonals for X or O victory.
	if (score == 0 and b[0][0] == b[1][1] and b[1][1] == b[2][2]) :
	
		if (b[0][0] == player) :
			score = 10
		elif (b[0][0] == opponent) :
			score = -10

	if (score == 0 and b[0][2] == b[1][1] and b[1][1] == b[2][0]) :
	
		if (b[0][2] == player) :
			score = 10
		elif (b[0][2] == opponent) :
			score = -10

	# Else if none of them have won then return 0
	return score

# This is the minimax function. It considers all
# the possible ways the game can go and returns
# the value of the board
def minimax(board, depth, isMax) :
	score = evaluate(board)

	# If Maximizer has won the game return his/her
	# evaluated score
	if (score == 10) :
		return score

	# If Minimizer has won the game return his/her
	# evaluated score
	if (score == -10) :
		return score

	# If there are no more moves and no winner then
	# it is a tie
	if (isMovesLeft(board) == False) :
		return 0

	# If this maximizer's move
	if (isMax) :	
		best = -1000

		# Traverse all cells
		for i in range(3) :		
			for j in range(3) :
			
				# Check if cell is empty
				if (board[i][j]=='_') :
				
					# Make the move
					board[i][j] = player

					# Call minimax recursively and choose
					# the maximum value
					best = max( best, minimax(board,
											depth + 1,
											not isMax) )

					# Undo the move
					board[i][j] = '_'
		return best

	# If this minimizer's move
	else :
		best = 1000

		# Traverse all cells
		for i in range(3) :		
			for j in range(3) :
			
				# Check if cell is empty
				if (board[i][j] == '_') :
				
					# Make the move
					board[i][j] = opponent

					# Call minimax recursively and choose
					# the minimum value
					best = min(best, minimax(board, depth + 1, not isMax))

					# Undo the move
					board[i][j] = '_'
		return best

# This will return the best possible move for the player
def findBestMove(board) :
	bestVal = -1000
	bestMove = (-1, -1)

	# Traverse all cells, evaluate minimax function for
	# all empty cells. And return the cell with optimal
	# value.
	for i in range(3) :	
		for j in range(3) :
		
			# Check if cell is empty
			if (board[i][j] == '_') :
			
				# Make the move
				board[i][j] = player

				# compute evaluation function for this
				# move.
				moveVal = minimax(board, 0, False)

				# Undo the move
				board[i][j] = '_'

				# If the value of the current move is
				# more than the best value, then update
				# best/
				if (moveVal > bestVal) :			
					bestMove = (i, j)
					bestVal = moveVal

	return bestMove

def switch_board_representation(board):
  new_board = [['_' for x in range(3)] for y in range(3)]
  for key, value in board.items():
    x, y = (int(key) - 1) % 3, 2 - (int(key) - 1) // 3
    if value == ' X ':
      new_board[y][x] = 'x'
    elif value == ' O ':
      new_board[y][x] = 'o'
  return new_board


board = {'7': '   ', '8': '   ', '9': '   ',
         '4': '   ', '5': '   ', '6': '   ',
         '1': '   ', '2': '   ', '3': '   '}

board_keys = []
filled = [False] * 10 
for key in board:
    board_keys.append(key)


def restartBoard(board):
    global filled
    filled = [False] * 10 
    for key in board_keys:
        board[key] = "   "


def printBoard(board):
    print(board['7'] + '|' + board['8'] + '|' + board['9'])
    print('-----------')
    print(board['4'] + '|' + board['5'] + '|' + board['6'])
    print('-----------')
    print(board['1'] + '|' + board['2'] + '|' + board['3'])


def checkWinner(board, jarvis,turn):
    if ((board['7'] == board['8'] == board['9'] != '   ')
		or (board['4'] == board['5'] == board['6'] != '   ')
		or (board['1'] == board['2'] == board['3'] != '   ')
		or (board['7'] == board['4'] == board['1'] != '   ')
		or (board['8'] == board['5'] == board['2'] != '   ')
		or (board['9'] == board['6'] == board['3'] != '   ')
		or (board['7'] == board['5'] == board['3'] != '   ')
		or (board['1'] == board['5'] == board['9'] != '   ')
        ):
        printBoard(board)
        jarvis.say("\n--- Game Over ---\n", Fore.GREEN)
        jarvis.say(turn + " won!", Fore.GREEN)
        return True
    else:
        return False


@plugin("tic_tac_toe")
def game(jarvis, s):
    print('The tic tac toe game for two players.')
    print('Positions on the board are placed as follow:')
    print('7 | 8 | 9\n-----------\n4 | 5 | 6\n-----------\n1 | 2 | 3')
    print('If you want to play against Jarvis press 1.')
    print('If you want to play with a friend next to you press 2.')

    game_type = input("Enter your game type, 1 or 2:\n")

    print('\n\n\nEnter the numbers on your keyboard to place your piece.')

    restartBoard(board)
    turn = ' X '
    count = 0
    


    while count < 10:
        printBoard(board)
        if (turn == ' X ' or game_type == '2'):
            s = jarvis.input(turn + "turn. " + "Choose a position!") #jarvis.input(turn + "turn. " + "Choose a position!", Fore.BLUE)
            if s not in board_keys:
                jarvis.say(
                    "Incorrect input. Please print any number from 1 to 9 corresponding to the position on the board!", Fore.RED)
                continue
        else:
            
            print(Fore.WHITE, "It's the bot turn!")
            new_board = switch_board_representation(board)
            bestMove = findBestMove(new_board)
            s = str(((2 - bestMove[0]) * 3 ) + (bestMove[1] + 1))

    
        if filled[int(s)] == False:
            print(Fore.WHITE)
            filled[int(s)] = True
            board[s] = turn
            count += 1
        else:
            print(Fore.RED)
            jarvis.say(
                "This position is already filled.\nChoose another position!", Fore.RED)
            continue

        if count >= 5:
            if(checkWinner(board, jarvis,turn)):
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