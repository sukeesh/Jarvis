# -*- coding: utf-8 -*-
import requests
import bs4
from plugin import plugin, require

# TODO: handle errors and instructions better


@require(network=True)
@plugin('lyrics')
class lyrics():
    """
    finds lyrics
    the format is song,artist
    song and artist are separated by a -
    -- Example:
        lyrics wonderful tonight-eric clapton
    """

    def __call__(self, jarvis, s):
        jarvis.say(self.find(s))

    # info[0] = song
    # info[1] = artist
    # info[2] = either options or album, depending on how i extend the
    # functionality
    def find(self, s):
        info = self.parse(s)
        # TODO: implement find album/song functions
        # TODO: implement actual searches in case of not knowing the correct
        # full name of song or artist

        artist = None
        song = None
        album = None

        if info:
            song = info[0]
            info.pop(0)
        if info:
            artist = info[0]
            info.pop(0)
        if info:
            album = info[0]
            info.pop(0)
        if not song or not artist:
            # error if artist or song don't exist
            return "you forgot to add either song name or artist name"
        response = get_lyric(artist, song)
        if response:
            return response
        else:
            return "Song or Singer does not exist or the API does not have lyrics"

    @classmethod
    def parse(self, s):
        # separate song/artist/album by a -
        information = s.split('-')
        return information


"""
All credit for this code goes to https://github.com/geekpradd
I only fixed some of the issues I was having with some requests,
but since he does not mantain his repository anymore and
forking it just to use it for this project was too much work
I just copied and fix the methods used in PyLyrics
"""


def get_lyric(singer, song):
    # Replace spaces with _
    singer = singer.replace(' ', '_')
    song = song.replace(' ', '_')
    url = 'http://lyrics.wikia.com/{0}:{1}'.format(singer, song)
    req = requests.get(url)
    s = bs4.BeautifulSoup(req.text, "lxml")
    # Get main lyrics holder
    lyrics = s.find("div", {'class': 'lyricbox'})
    if lyrics is None:
        return None
    # Remove Scripts
    [k.extract() for k in lyrics('script')]
    # Remove comments
    comments = lyrics.findAll(text=lambda text: isinstance(text, bs4.Comment))
    # for c in comments:
    #     c.extract()
    # Remove unecessary tags
    for tag in ['div', 'i', 'b', 'a']:
        for match in lyrics.findAll(tag):
            match.replaceWithChildren()

    # TODO: check if you need the encode/decode thing, if you do then do a try
    # catch for it

    # get output as string and remove non unicode characters and replace <br> with newlines
    # output = str(lyrics).encode('utf-8', errors = 'replace')[22:-6:] \
    #     .decode('utf-8').replace('\n','').replace('<br/>','\n')
    output = str(lyrics).replace('\n', '').replace('<br/>', '\n')[22:-6:]
    try:
        return output
    except BaseException:
        return output.encode('utf-8')
