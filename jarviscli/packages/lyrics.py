# -*- coding: utf-8 -*-
from PyLyrics import *
from utilities.PyLyricsClone import py_lyrics

#TODO: handle errors and instructions better

class lyrics(object):
    def __init__(self):
        self.lyrics = py_lyrics()
        self.song = None
        self.artist = None
        self.album = None

    def find(self, s):
        info = self.parse(s)
        #info 0 = song
        #info 1 = artist
        #info 2 = album
        #TODO: implement find album/song functions
        if info:
            self.song = info[0]
            info.pop(0)
        if info:
            self.artist = info[0]
            info.pop(0)
        if info:
            self.album = info[0]
            info.pop(0)
        if not self.song or not self.artist:
            #error if artist or song don't exist
            return "you forgot to add either song name or artist name"
        response = self.lyrics.get_lyric(self.artist, self.song)
        if response:
            return self.lyrics.get_lyric(self.artist, self.song)
        else:
            return "Song or Singer does not exist or the API does not have lyrics"


    def parse(self, s):
        #separate song/artist/album by a -
        information = s.split('-')
        return information
