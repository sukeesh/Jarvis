import os
from plugin import plugin

@plugin('open')
def open(jarvis,s):
	if(s != ""):
		string = "xdg-open " + "/usr/share/applications/" + s + ".desktop"
		os.system(string)
	else:
		jarvis.say("avaliable options are:")
		os.system("ls -1 /usr/share/applications/ | sed -e 's/\.desktop$//'")
@plugin('terminal')
def run(jarvis): 
	os.system("xfce4-terminal")
