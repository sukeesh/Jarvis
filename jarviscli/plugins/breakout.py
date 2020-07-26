import copy
import keyboard
import os
import time
from pynput import keyboard
from plugin import plugin
from multiprocessing import Process

isRight= 0
isLeft= 0
terminate = 0


def on_press(key):
    global  isRight
    global  isLeft
    global terminate
    if key == keyboard.Key.a:
        isLeft = 1
        isRight = 0
    elif key == keyboard.Key.d:
        isRight = 1
        isLeft = 0
    elif key == keyboard.Key.p:
        terminate = 1
        print(terminate)


@plugin('breakout')
def breakoutRunner(jarvis, s):
    with keyboard.Listener(
            on_press=on_press) as listener:
        listener.join()
    listener.start()
    while 1:
        a = 3
    # p1 = Process(target=breakout())
    # p2 = Process(target=breakoutListener())

    # p1.start()
    # p1.join()
    # p2.start()

def breakoutListener():
    global terminate
    global isRight
    global isLeft
    while 1:
        if terminate :
            break
        if keyboard.is_pressed('a'):
            isRight = 0
            isLeft = 1
        if keyboard.is_pressed('d'):
            isRight = 1
            isLeft = 0
        if keyboard.is_pressed("e"):
            terminate = 1

def breakout():
    global terminate
    numScores = 0
    game_board_template = [
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['#', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', '#'],
        ['#', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', '#'],
        ['#', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', '#'],
        ['#', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '*', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '_', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']]
    game_board = copy.deepcopy(game_board_template)
    vx = -1
    vy = -1
    ball_y = 7
    ball_x = 10
    paddle_y = 9
    paddle_x = 10
    while 1:
        if numScores ==68:
            print("YOU WON!")
            break
        os.system('cls')
        if terminate :
            break
        if isRight:
            game_board[paddle_y][paddle_x] = ' '
            paddle_x = paddle_x + 1
            game_board[paddle_y][paddle_x] = '_'
        if isLeft:
            game_board[paddle_y][paddle_x] = ' '
            paddle_x = paddle_x - 1
            game_board[paddle_y][paddle_x] = '_'
        if ball_x >= 19 or ball_x <= 1:
            vx *= -1
        if ball_y <= 1 or game_board[ball_y][ball_x] == '-':
            numScores+=1
            vy *= -1
        if game_board[ball_y][ball_x] == '_':
            vy *= -1
        if ball_y >= 10:
            print("life decreased")
        game_board[ball_y][ball_x] = ' '
        ball_x += vx
        ball_y += vy
        game_board[ball_y][ball_x] = '*'
        print('\n'.join([''.join(i) for i in game_board]))
        time.sleep(0.1)
