
from plugin import plugin
from collections import deque #Store info on player move
import curses # UI/UX

playerTurn = 0 #Global Variable

xPositions = deque(maxlen=3)
oPositions = deque(maxlen=3)

def removeLast(win, xQue, oQue, cord, letter):
    if letter == ord('O'):
        if len(oQue) == oQue.maxlen:
            oldY, oldX = oQue.popleft() 
            win.addstr(oldY, oldX, " ") 
        oQue.append(cord)
        
        # Highlight
        if len(oQue) > 2:
            oldY, oldX = oQue[0]
            win.addstr(oldY, oldX, "O", curses.color_pair(3) | curses.A_BOLD)  # Highlight
        win.refresh()

    elif letter == ord('X'):
        if len(xQue) == xQue.maxlen:
            oldY, oldX = xQue.popleft()  
            win.addstr(oldY, oldX, " ")  
        xQue.append(cord) 
        
        # Highlight
        if len(xQue) > 2:
            oldY, oldX = xQue[0]
            win.addstr(oldY, oldX, "X", curses.color_pair(3) | curses.A_BOLD)  # Highlight
        win.refresh()


def checkWin(win, A): #Guys I might just be the smartest person on earth (Thanks chatGPT for the help in figuring out how to do this)

    winCondition = [
[(3, 5), (3, 7), (3, 9)], #TOP 
[(5, 5), (5, 7), (5, 9)], #MIDDLE
[(7, 5), (7, 7), (7, 9)], #BOTTOM 
[(3, 5), (5, 5), (7, 5)], #LEFT
[(3, 7), (5, 7), (7, 7)],  #MIDDLE
[(3, 9), (5, 9), (7, 9)], #RIGHT
[(7, 5), (5, 7), (3, 9)],  # /
[(3, 5), (5, 7), (7, 9)]  # \
    ]

    for condition in winCondition:
        if all(win.inch(y, x) & curses.A_CHARTEXT == A for y, x in condition):
            return True

    return False


def setupGame(win):
    global playerTurn
    global oPositions
    global xPositions

    xPositions.clear()
    oPositions.clear()

    playerTurn = 0

    win.clear()
    win.addstr(1, 3, "'X' Starts! ")
    win.addstr(10, 0, "INSTRUCTIONS: ")
    win.addstr(11, 0, "PRESS 'q' TO EXIT PROGRAM")
    win.addstr(12, 0, "PRESS 'c' TO CLEAR THE BOARD")
    win.addstr(13, 0, "PRESS 'x' or 'o' TO PLACE CHARACTER")
    win.addstr(14, 0, "ARROW KEYS TO MOVE AROUND")
    for y in range(2, 9, 1): #just change these numbers by 2 to make a bigger grid
        match y % 2:
            case 0:
                for x in range(4, 11, 1):
                    win.addstr(y, x, '-')
            case 1:
                for x in range(4, 11, 2):
                    win.addstr(y, x, '|')
    x, y = 7, 5
    win.move(y, x)
    win.refresh()

def main(stdscr): # MAIN FUNCTION
    global playerTurn
    global xPositions
    global oPositions

    curses.start_color() #Let's us use color
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    win = curses.newwin(20, 40, 0, 0) #Creates the main window

    win.keypad(True)
    curses.mousemask(0)
    win.border()
    setupGame(win)
    win.refresh()
    x, y = 7, 5 #Center of game grid

    while True:
        key = win.getch()

        if key == ord('q'): #Quit Game
            break

        elif key == ord('c'): #Clear Board
            setupGame(win)
            x, y = 7, 5

        elif key == ord('x') and playerTurn == 0: #Add 'X' at given cursor position

            if win.inch(y, x) == ord(' '):
                letter = ord('X')
                removeLast(win, xPositions, oPositions, (y, x), letter)
                win.addstr(1, 3, "'O's Turn!  ")
                win.addstr(y, x, 'X', curses.color_pair(1) | curses.A_BOLD)
                win.move(y, x)
                win.refresh()

                if checkWin(win, letter):
                    playerTurn = -1
                    win.addstr(1, 3, "X WINS! CONGRATS!")

                else:
                    playerTurn += 1

                win.move(y, x)
                win.refresh()

            else:
                win.addstr(1, 3, "No Cheating!")
                win.move(y, x)
                win.refresh()

        elif key == ord('o') and playerTurn == 1: #Add 'O' at given cursor position

            if win.inch(y, x) == ord(' '):
                letter = ord('O')
                removeLast(win, xPositions, oPositions, (y, x), letter)
                win.addstr(1, 3, "'X's Turn!  ")
                win.addstr(y, x, 'O', curses.color_pair(2) | curses.A_BOLD)
                win.move(y, x)
                win.refresh()


                if checkWin(win, letter):
                    playerTurn = -1
                    win.addstr(1, 3, "O WINS! CONGRATS!")

                else:
                    playerTurn -= 1

                win.move(y, x)
                win.refresh()

            else:
                win.addstr(1, 3, "No Cheating!")
                win.move(y, x)
                win.refresh()

        elif key == curses.KEY_UP: #Move cursor UP
            y -= 2

            if y <= 2: #BOUNDS CHECK
                y += 2

            win.move(y, x)
            win.refresh()

        elif key == curses.KEY_DOWN: #Move cursor DOWN
            y += 2

            if y >= 9: #BOUNDS CHECK
                y -= 2

            win.move(y, x)
            win.refresh()

        elif key == curses.KEY_RIGHT: #Move cursor RIGHT
            x += 2

            if x >= 11: #BOUNDS CHECK
                x -= 2

            win.move(y, x)
            win.refresh()

        elif key == curses.KEY_LEFT: #Move cursor LEFT
            x -= 2

            if x <= 4: #BOUNDS CHECK
                x += 2

            win.move(y, x)
            win.refresh()

@plugin("tac_toe")
def game(jarvis, s):
    curses.wrapper(main)
