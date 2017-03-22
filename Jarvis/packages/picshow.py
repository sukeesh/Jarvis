# -*- coding: utf-8 -*-
import webbrowser

def showpics(strr):
    strr = strr.split(" ")
    query = strr[4]
    url = "https://www.google.com/search?tbm=isch&q={}".format(query)
    webbrowser.open(url)
