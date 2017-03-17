import os, glob, re
from colorama import Fore
from colorama import init
import instantmusic

def play(data):
    if len(data[5:]) == 0:
        print(Fore.BLUE + "Song name doesn't exist. (music '"'song name'"') " + Fore.RESET)
    else:
        song = data[6:]
        music = os.system("ls | grep -i " +'"'+ song +'"' +" >> music.txt")
        txt = open("music.txt", "r+")
        isthere = txt.readlines()

        if len(isthere) == 0:
            os.system("instantmusic -s " + song)
            play(data)
        else:
            song = isthere[0]
            song = song.replace("\n", "")
            newname = re.sub(r'\([^)]*\)', '', song).replace("-", "").replace("_", "")
            os.renames(song, newname)
            os.system("xdg-open " + newname.replace(" ", "\ "))
            txt.seek(0)
            txt.truncate()