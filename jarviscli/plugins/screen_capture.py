import pyautogui as pg
from jarviscli import entrypoint


@entrypoint
def screencapture(jarvis, s):
    """
    By holding Ctrl + Alt + Shift + R key we start screen capture in
    """

    def engine():
        pg.keyDown("ctrl")
        pg.keyDown("alt")
        pg.keyDown("shift")
        pg.press("r")
        pg.keyDown("shift")
        pg.keyUp("alt")
        pg.keyUp("ctrl")

    jarvis.say('Screen Recording Started')
    engine()
    n = input("Press Q to stop : ")
    if n == 'Q':
        engine()
        jarvis.say('Screen Recording Ended')
