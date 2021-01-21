import os

from plugin import Platform, plugin, require


@require(platform=Platform.LINUX)
@plugin('open')
def open(jarvis, s):

    if(s != ""):
        string = "gtk-launch " + "/usr/share/applications/" + s + ".desktop"
        os.system(string)
    else:
        jarvis.say("avaliable options are:")
        os.system("ls -1 /usr/share/applications/ | sed -e 's/\\.desktop$//'")
