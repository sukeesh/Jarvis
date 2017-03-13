import webbrowser

def showpics(strr):
    strr = strr.split(" ")
    query = strr[4]
    url = "https://www.google.co.in/search?tbm=isch&q={}".format(query)
    webbrowser.open(url)
