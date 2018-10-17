# -*- coding: utf-8 -*-
from utilities.PyLyricsClone import py_lyrics
from plugin import Plugin

# TODO: handle errors and instructions better


class lyrics(Plugin):
    """
    finds lyrics
    the format is song,artist
    song and artist are separated by a -
    -- Example:
        lyrics wonderful tonight-eric clapton
    """
    def __init__(self):
        self.lyrics = py_lyrics()
        self.song = None
        self.artist = None
        self.album = None

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        jarvis.say(self.find(s))

    # info[0] = song
    # info[1] = artist
    # info[2] = either options or album, depending on how i extend the functionality
    def find(self, s):
        info = self.parse(s)
        # TODO: implement find album/song functions
        # TODO: implement actual searches in case of not knowing the correct full name of song or artist
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
            # error if artist or song don't exist
            return "you forgot to add either song name or artist name"
        response = self.lyrics.get_lyric(self.artist, self.song)
        if response:
            return response
        else:
            return "Song or Singer does not exist or the API does not have lyrics"

    @classmethod
    def parse(self, s):
        # separate song/artist/album by a -
        information = s.split('-')
        return information
