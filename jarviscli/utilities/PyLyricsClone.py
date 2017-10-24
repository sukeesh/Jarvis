# -*- coding: utf-8 -*-
"""
All credit for this code goes to https://github.com/geekpradd
I only fixed some of the issues I was having with some requests,
but since he does not mantain his repository anymore and
forking it just to use it for this project was too much work
I just copied and fix the methods used in PyLyrics
"""
import requests
from bs4 import BeautifulSoup, Comment


class py_lyrics(object):
    def __init__(self):
        pass

    @classmethod
    def get_track(self, album):
        url = "http://lyrics.wikia.com/api.php?action=lyrics&artist={0}&fmt=xml".format(
            album.artist())
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        currentAlbum = None
        for al in soup.find_all('album'):
            if al.text.lower().strip() == album.name.strip().lower():
                currentAlbum = al
                break
        songs = [Track(song.text, album, album.artist())
                 for song in currentAlbum.findNext('songs').findAll('item')]
        return songs

    @classmethod
    def get_albums(self, singer):
        singer = singer.replace(' ', '_')
        url = 'http://lyrics.wikia.com/{0}'.format(singer)
        s = BeautifulSoup(requests.get(url), "lxml")
        spans = s.findAll('span', {'class': 'mw-headline'})
        albums = []
        for tag in spans:
            a = tag.findAll('a')[0]
            albums.append(
                Album(a.text, 'http://lyrics.wikia.com' + a['href'], singer))
        if not albums:
            return None
        return albums

    @classmethod
    def get_lyric(self, singer, song):
        # Replace spaces with _
        singer = singer.replace(' ', '_')
        song = song.replace(' ', '_')
        url = 'http://lyrics.wikia.com/{0}:{1}'.format(singer, song)
        req = requests.get(url)
        s = BeautifulSoup(req.text, "lxml")
        # Get main lyrics holder
        lyrics = s.find("div", {'class': 'lyricbox'})
        if lyrics is None:
            return None
        # Remove Scripts
        [s.extract() for s in lyrics('script')]
        # Remove comments
        comments = lyrics.findAll(text=lambda text: isinstance(text, Comment))
        # Remove unecessary tags
        for tag in ['div', 'i', 'b', 'a']:
            for match in lyrics.findAll(tag):
                match.replaceWithChildren()

        # TODO: check if you need the encode/decode thing, if you do then do a try catch for it

        # get output as string and remove non unicode characters and replace <br> with newlines
        # output = str(lyrics).encode('utf-8', errors = 'replace')[22:-6:].decode('utf-8').replace('\n','').replace('<br/>','\n')
        output = str(lyrics).replace('\n', '').replace('<br/>', '\n')[22:-6:]
        try:
            return output
        except:
            return output.encode('utf-8')
