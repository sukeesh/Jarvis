import os
from colorama import Fore

from plugin import plugin, alias, require, LINUX


def find_cached_music(music):
    find = os.popen("ls music -tc")
    music = str(find.readline()).replace("\n", "")
    music = music.replace(" ", "\\ ").replace(
        " (", " \\("). replace(")", "\\)")
    return music


@alias("music")
@require(platform=LINUX)
@plugin('play')
def play(jarvis, data):
    """
    Jarvis will find, download and play any song you want
    If ffmpeg is installed, songs will be downloaded as .mp3 instead .webm
    -- Example:
        music wonderful tonight
        play eye of the tiger
    """

    if not data:
        jarvis.say("Missing parameter: Song name", Fore.BLUE)

    else:
        music = find_cached_music(data)

        # Try download if not exists
        if not music:
            os.system(
                "cd music && instantmusic -s '"
                + data
                + "' 2> /dev/null")
            music = find_cached_music(data)

        # Try play if exists
        if not music:
            jarvis.say("Something seems to went wrong...", Fore.BLUE)
        else:
            os.system(
                "XDG_CURRENT_DESKTOP= DESKTOP_SESSION= xdg-open music/"
                + music
                + " 2> /dev/null")
