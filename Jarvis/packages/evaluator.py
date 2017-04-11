# -*- coding: utf-8 -*-
from utilities.GeneralUtilities import print_say

def calc(s, self):
    s = str.lower(s)
    s = s.replace("power", "**")
    s = s.replace("plus", "+")
    s = s.replace("minus", "-")
    s = s.replace("divided by", "/")
    s = s.replace("by", "/")
    s = s.replace("^", "**")
    try:
        x = eval(s)
        print_say(x, self)
    except Exception:
        print_say("Error : Not in correct format", self)
