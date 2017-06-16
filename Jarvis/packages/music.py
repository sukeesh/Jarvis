# -*- coding: utf-8 -*-

import os
from colorama import Fore


def play(data):
    if len(data) == 0:
        print(Fore.BLUE + "Song name doesn't exist. (music '"'song name'"') " + Fore.RESET)

    else:
        wanted = data
        find = os.popen("ls | grep -i " +'"'+ wanted +'"')
        music = str(find.readline())

        if not music:
            os.system("instantmusic -s " + wanted)
            find = os.popen("ls -tc --hide='__*' --hide='*.py'")
            music = str(find.readline()).replace("\n", "")
            os.system("XDG_CURRENT_DESKTOP= DESKTOP_SESSION= xdg-open " + music.replace(" ", "\ ").replace(" (", " \("). replace(")", "\)"))

        else:
            os.system("XDG_CURRENT_DESKTOP= DESKTOP_SESSION= xdg-open " + music.replace(" ", "\ ").replace(" (", " \("). replace(")", "\)"))