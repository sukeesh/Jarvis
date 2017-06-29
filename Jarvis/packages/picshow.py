# -*- coding: utf-8 -*-
import webbrowser


def showpics(string):
    string = string.split(" ")
    query = string[4]
    url = "https://www.google.com/search?tbm=isch&q={}".format(query)
    webbrowser.open(url)
