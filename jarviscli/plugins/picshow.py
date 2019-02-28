# -*- coding: utf-8 -*-
import webbrowser
from plugin import plugin, require, alias


@alias('show pics')
@require(network=True)
@plugin('display pics')
def display_pics(jarvis, string):
    """
    Displays photos of the topic you choose.
    -- Example:
        display pics of castles
    """
    url = "https://www.google.com/search?tbm=isch&q={}".format(
        string.replace("of", ""))
    webbrowser.open(url)
