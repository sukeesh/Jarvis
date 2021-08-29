from plugin import plugin, require, alias
import os
import sys
import subprocess
import platform
import pyautogui


@alias("capture", "screen")
@plugin('screen_capture')
def capture_screen(jarvis, s):

    if (platform.system() == 'Linux'):
        proc = subprocess.Popen(['dpkg',
                                 '-s',
                                 'scrot'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, _ = proc.communicate()
        if not(out.decode("utf-8")):
            print("Package Not Installed.")
            print("***************************\n")

            print(
                "Please install the following package for proper functioning of the screenshot function: \n")
            print("1. 'sudo apt-get install scrot'\n")

            print("***************************\n")
            sys.exit()
    jarvis.say("Please specify the path: ")
    path = jarvis.input()
    image = pyautogui.screenshot()
    image.save(os.path.join(path, "screen.png"))
    jarvis.say("Done, check your path.")
