# -*- coding: utf-8 -*-
import webbrowser
import requests
from bs4 import BeautifulSoup
from colorama import Fore


def show_news():

    url = "https://news.google.com/"
    wp = requests.get(url)
    soup = BeautifulSoup(wp.text, "lxml")
    title_to_be_shown = soup.findAll("span")
    cnt = 1
    title_contents = []
    parent_urls = []

    for i in title_to_be_shown:
        if i.get('class')!=None and "titletext" in i.get('class'):
            title_contents.append(str(i.get_text()))
            parent_urls.append(str(i.parent['url']))
            cnt += 1
            if cnt == 5:
                break

    news_contents = []
    divs = soup.findAll("div")
    cnt = 1
    for i in divs:
        if i.get('class')!=None and "esc-lead-snippet-wrapper" in i.get('class'):
            news_contents.append(str(i.get_text()))
            cnt += 1
            if cnt == 5:
                break

    i = 0
    while i < len(title_contents):
        print (Fore.GREEN + str(i + 1) + " - " + title_contents[i] + Fore.RESET)
        i += 1

    print("Type index to expand news\n")
    try:
        idx = int(raw_input())
    except:
        idx = int(input())
    idx -= 1
    print(">> {0} {1} {2}\n".format(Fore.BLUE, news_contents[idx], Fore.RESET))
    print("{0}\n Do you want to read more? (yes/no): {1}".format(Fore.RED, Fore.RESET))
    try:
        take_yn = raw_input()
    except:
        take_yn = input()

    if take_yn.lower() == "yes":
        webbrowser.open(parent_urls[idx])
    else:
        return
