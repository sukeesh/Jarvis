from plugin import plugin, require
from colorama import Fore

import sys
import spotipy
import spotipy.util as util

SPOTIPY_CLIENT_ID = '865dcb503fc8489d9a2366b5fc0dc58d'
SPOTIPY_CLIENT_SECRET = '898fbca894d6401785d5f061771fa25d'
REDIRECT_URI = 'http://localhost:8080'
scope = 'user-read-playback-state user-library-read user-modify-playback-state user-read-currently-playing'


@require(network=True)
@plugin('spotify')
class Spotify:
    """
    This plugin can manage your Spotify music on any device

    example: spotify play track Never gonna give you up, powered by Pierrecoulon1
    """

    def __call__(self, jarvis, s):
        s = s.split(' ', 1)
        if (len(s) == 0):
            jarvis.say(
                "Invalid params. Try: 'spotify help' for more information", Fore.RED)
        if (s[0] == "help"):
            self.print_help(jarvis)
            return
        token = util.prompt_for_user_token(
            '', scope, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, REDIRECT_URI)
        if token:
            sp = spotipy.Spotify(auth=token)
            if (s[0] == "play"):
                if (len(s) > 1):
                    s = [s[0]] + s[1].split(' ', 1)
                    if (s[1] in ["album", "artist", "track", "playlist", "show", "episode"] and len(s) > 2):
                        self.play_uri(jarvis, sp, s[2], s[1])
                    else:
                        jarvis.say(
                            "Invalid play option. Try: 'spotify help' for more information", Fore.RED)
                else:
                    self.play(jarvis, sp)
            elif (s[0] == "pause"):
                self.pause(jarvis, sp)
            elif (s[0] == "add" and len(s) > 1):
                self.add(jarvis, sp, s[1])
            elif (s[0] == "song"):
                self.song(jarvis, sp)
            elif (s[0] == "next"):
                self.next(jarvis, sp)
            else:
                jarvis.say(
                    "Invalid option. Try: 'spotify help' for more information", Fore.RED)
        else:
            jarvis.say("Can't get token", Fore.RED)

    def pause(self, jarvis, sp):
        try:
            sp.pause_playback()
            jarvis.say("OK", Fore.GREEN)
        except:
            return

    def next(self, jarvis, sp):
        try:
            sp.next_track()
            jarvis.say("OK", Fore.GREEN)
        except:
            return

    def play(self, jarvis, sp, context=None, uris=None):
        try:
            sp.start_playback(context_uri=context, uris=uris)
            jarvis.say("OK", Fore.GREEN)
        except:
            return

    def search(self, jarvis, sp, q, t='track'):
        try:
            return sp.search(q, type=t)
        except:
            return None

    def add(self, jarvis, sp, track):
        try:
            result = self.search(jarvis, sp, track)
            if (not result or len(result['tracks']['items']) == 0):
                jarvis.say("Track does not found", Fore.RED)
                return
            sp.add_to_queue(result['tracks']['items'][0]['uri'])
            jarvis.say("OK", Fore.GREEN)
        except:
            return

    def play_uri(self, jarvis, sp, q, t):
        try:
            result = self.search(jarvis, sp, q, t)
            if (not result or len(result[t + 's']['items']) == 0):
                jarvis.say(f"{t.capitalize()} does not found", Fore.RED)
            if (t == "track" or t == "episode"):
                self.play(jarvis, sp, uris=[
                          result[t + 's']['items'][0]['uri']])
            else:
                self.play(
                    jarvis, sp, context=result[t + 's']['items'][0]['uri'])
        except:
            return

    def song(self, jarvis, sp):
        try:
            track = sp.current_user_playing_track()
            if (not track):
                jarvis.say("No track is playing", Fore.RED)
                return
            artists = []
            try:
                for i in track['item']['artists']:
                    artists.append(i['name'])
            except:
                artists = []
            artists = ", ".join(artists) if len(artists) > 0 else "Unknown artist"
            try:
                album = track['item']['album']['name']
            except:
                album = "Unknown album"
            try:
                name = track['item']['name']
            except:
                name = "Unknown music"
            jarvis.say(f"Playing: {album} - {artists}: {name}")
        except:
            return
    
    def print_help(self, jarvis):
        jarvis.say("USAGE: spotify <option>")
        jarvis.say("Spotify option:")
        jarvis.say(
            "    play [type item]    Start or resume user's playback. Valid types of the item are")
        jarvis.say(
            "                        'artist', 'album', 'track', 'playlist', 'show' or 'episode'")
        jarvis.say("    pause               Pause user's playback")
        jarvis.say(
            "    add <song>          Adds a song to the end of a user's queue")
        jarvis.say(
            "    song                Get information about the current users currently playing track")
        jarvis.say("    next                Skip user's playback to next track")
        jarvis.say("    help                Display this help")
