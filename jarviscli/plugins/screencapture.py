import os

import pyautogui

from plugin import alias, plugin, require


@require(native='scrot')
@alias("capture", "screen")
@plugin('screen_capture')
def capture_screen(jarvis, s):
    jarvis.say("Please specify the path: ")
    path = jarvis.input()
    image = pyautogui.screenshot()
    image.save(os.path.join(path, "screen.png"))
    jarvis.say("Done, check your path.")
