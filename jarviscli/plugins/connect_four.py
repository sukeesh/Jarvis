from plugin import plugin

# General values for connect 4 game and board
numberRows = 6
numberColumns = 7
numToWin = 4
GameBoard = [[0] * numberColumns for j in range(numberRows)]
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def restartBoard():
    for i in range(numberRows):
        for j in range(numberColumns):
            GameBoard[i][j] = str(' ')


# Function to check if the column is open
def checkIfFree(c):
    if whatsAtPos(0, c) == ' ':
        return True
    else:
        return False


# Function that calls all win conditions
def checkForWin(c):
    for i in range(numberRows):
        if whatsAtPos(i, c) != ' ':
            row = i
            if checkHorizWin(row, c, whatsAtPos(row, c)) \
                    or checkVertWin(row, c, whatsAtPos(row, c)) \
                    or checkDiagWin(row, c, whatsAtPos(row, c)):
                return True
            break

    return False


# Place token at the lowest available row in the selected column
def placeToken(p, c):
    startIndex = numberRows - 1
    stopIndex = -1
    step = -1
    # Loop through column to find top most available row to place token
    for i in range(startIndex, stopIndex, step):
        if whatsAtPos(i, c) == ' ':
            GameBoard[i][c] = str(p)
            break


# Check for a horizontal win
def checkHorizWin(r, c, p):
    # Temp row and col values to manipulate throughout function
    row = r
    col = c

    # Count matching tokens to the right. Stop when at end of board
    rightCounter = 0
    while col < numberColumns:
        if whatsAtPos(row, col) == p:
            rightCounter += 1
        else:
            row = r
            break
        col += 1

    # Count matching tokens to the left. Stop when at end of board
    leftCounter = 0
    col = c
    while col >= 0:
        # break if at first column
        if col == 0:
            break
        col -= 1
        if whatsAtPos(row, col) == p:
            leftCounter += 1
        else:
            break

    # Add left and right together to check if numToWin was reached
    if leftCounter + rightCounter >= numToWin:
        print("Congrats, player ", p, " you win horizontally!\n")
        return True
    else:
        return False


def checkVertWin(r, c, p):
    winCheck = False
    counter = 0

    if r > numberRows - numToWin:
        return False
    for i in range(r, numberRows, 1):
        if whatsAtPos(i, c) == p:
            counter += 1
        else:
            counter = 0

        if counter == numToWin:
            winCheck = True
            print("Congrats, player ", p, ", you win vertically!\n")
            break

    return winCheck


def checkDiagWin(r, c, p):
    row = r
    col = c
    upRight = 0
    while row >= 0 and col <= numberColumns:
        if whatsAtPos(row, col) == p:
            upRight += 1
        else:
            row = r
            col = c
            break
        # If the column is he last column on the board, break the loop
        if col == numberColumns - 1 or row == 0:
            row = r
            col = c
            break

        row -= 1
        col += 1

    downLeft = 0
    while row < numberRows - 1 and col > 0:
        row += 1
        col -= 1
        if whatsAtPos(row, col) == p:
            downLeft += 1
        else:
            row = r
            col = c
            break
    if upRight + downLeft >= numToWin:
        print('Congrats! You won diagonally!')
        return True

    upLeft = 0
    while row >= 0 and col >= 0:
        if whatsAtPos(row, col) == p:
            upLeft += 1
        else:
            row = r
            col = c
            break

        if col == 0 or row == 0:
            row = r
            col = c
            break
        row -= 1
        col -= 1

    downRight = 0
    while row < numberRows - 1 and col < numberColumns - 1:
        row += 1
        col += 1
        if whatsAtPos(row, col) == p:
            downRight += 1
        else:
            break
    if downRight + upLeft >= numToWin:
        print("Congrats, player ", p, " you win diagonally!\n")
        return True

    return False


# Function to return value of gameboard location
def whatsAtPos(r, c):
    if GameBoard[r][c] == 'X':
        return f"{RED}X{RESET}"
    elif GameBoard[r][c] == 'O':
        return f"{YELLOW}O{RESET}"
    elif GameBoard[r][c] == ' ':
        return ' '
    else:
        return str(GameBoard[r][c])


# Check to see if players tied
def checkTie():
    startIndex = 0
    # players have not tied if there is still an empty place in the first row
    for i in range(startIndex, numberColumns, 1):
        if checkIfFree(i):
            return False
    # If there is no space left and checkForWin already passed the players tied
    print('Tie game! Thanks for playing!\n')
    return True


# Function to print the gameboard
def printBoard():
    ss = ''
    startIndex = 0

    # Create column headers (1-7)
    for i in range(startIndex, numberColumns, 1):
        ss += '|'
        ss = ss + str(i + 1)
    ss += '|'
    ss += '\n'

    # Create current GameBoard
    startIndex = 0
    startIndex_j = 0
    for i in range(startIndex, numberRows, 1):
        for j in range(startIndex_j, numberColumns, 1):
            ss += '|'
            ss = ss + str(whatsAtPos(i, j))
        ss += '|'
        ss += '\n'

    print(ss)


@plugin("connect_four")
def game(jarvis, s):
    # Welcome message and rules explanation
    print('Welcome to Connect Four! This is a two player game.\n')
    print('Enter numbers to place your token in the corresponding column!\n')
    print('Match four of your tokens in a row to win. Good Luck!\n')

    playerTracker = 0
    playAgainFlag = 'y'

    while playAgainFlag == 'y':
        restartBoard()

        printBoard()
        while True:

            # Make sure column is numeric.
            #  If not then ask user for numeric input again instead of throwing error.
            notNumericInputFlag = True
            while notNumericInputFlag == True:
                try:
                    column = int(input('Pick a column (1-7):\n'))
                    notNumericInputFlag = False
                except ValueError:
                    print("Enter a valid numeric input.")
            column -= 1

            # Make sure column is inbounds
            while column < 0 or column > numberColumns:
                print('Out of bounds. Pick another column.')
                printBoard()
                column = int(input('Pick a column (1-7):\n'))
                column -= 1

            # Make sure column is empty
            while not checkIfFree(column):
                print('Column is full. Pick another.\n')
                printBoard()
                column = int(input('Pick a column (1-7):\n'))
                column -= 1

            # get the players turn and place token now that conditions are met
            if playerTracker % 2 == 0:
                placeToken("X", column)
            else:
                placeToken("O", column)

            # print updated gameboard
            printBoard()

            # Check for a win on the last move
            if checkForWin(column):
                break

            # Make sure no one tied with the last move
            if checkTie():
                break

            # increment player tracker
            playerTracker += 1

        playAgainFlag = input('Would you like the play again? (Y/N)\n')
        playAgainFlag = playAgainFlag.strip()
        playAgainFlag = playAgainFlag.lower()
        while playAgainFlag != 'n' and playAgainFlag != 'y':
            playAgainFlag = input('Please enter Y or N\n')
            playAgainFlag = playAgainFlag.strip()
            playAgainFlag = playAgainFlag.lower()

    print('Thanks for playing!\n')


if __name__ == "__main__":
    game()
