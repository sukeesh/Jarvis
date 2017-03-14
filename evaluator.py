# -*- coding: utf-8 -*-

def calc(s):
    s = str.lower(s)
    s = s.replace("power", "**")
    s = s.replace("plus", "+")
    s = s.replace("minus", "-")
    s = s.replace("divided by", "/")
    s = s.replace("by", "/")
    s = s.replace("^", "**")
    try:
        x = eval(s)
        print(x)
    except Exception:
        print("Error : Not in correct format")

