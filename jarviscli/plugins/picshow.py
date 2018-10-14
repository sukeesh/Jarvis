# -*- coding: utf-8 -*-
import webbrowser


def showpics(string):
    url = "https://www.google.com/search?tbm=isch&q={}".format(
        string.replace("of", ""))
    webbrowser.open(url)
