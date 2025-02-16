from plugin import plugin, require
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Set up your credentials
client_id = '9432469329f94c449bc36b3273f7285a'
client_secret = '35d017ceebeb4eea83cd74ff5ee091ac'

# Set up the Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@require(network=True)
@plugin("topmusic")
class topmusic:
    """
    Plugin to extract top music tracks by genre using Spotify API
    """

    def __call__(self, jarvis, genre):
        valid_genre_list = [
            "pop", "rock", "hip-hop", "r&b", "country", "electronic", "jazz",
            "classical", "latin", "indie", "alternative", "metal", "blues", "reggae",
            "folk", "punk", "k-pop", "ambient", "edm", "trap", "lo-fi",
            "synthwave", "indie rock", "pop rock", "r&b", "reggaeton", "grunge", "disco"
        ]

        genre = genre.lower()

        if genre == "help":
            jarvis.say("List of possible top music genres: \n")
            index = 1
            for genre in valid_genre_list:
                jarvis.say(f"{index}. {genre}")
                index += 1
            jarvis.say("")
        elif genre not in valid_genre_list:
            jarvis.say("\nPlease run the command with a valid genre.\nValid input examples: topmusic jazz, topmusic pop\n\nType \"topmusic help\" for a list of music genres.\n")
        else:
            top_tracks = self.get_top_tracks_by_genre(jarvis, genre)
            if top_tracks:
                jarvis.say(f"Top 10 {genre.capitalize()} tracks:")
                for i, track in enumerate(top_tracks, 1):
                    jarvis.say(f"{i}. {track['name']} by {track['artist']} (Album: {track['album']})")
            else:
                jarvis.say(f"No tracks found for genre: {genre}")

    def get_top_tracks_by_genre(self, jarvis, genre):
        limit = 10
        search_queries = [
            f'genre:{genre}',
            genre,
            f'{genre} playlist'
        ]

        playlist_id = None
        for query in search_queries:
            try:
                results = sp.search(q=query, type='playlist', limit=1)
                if results and 'playlists' in results and results['playlists']['items']:
                    playlist_id = results['playlists']['items'][0]['id']
                    break
            except Exception as e:
                jarvis.say(f"Error during search: {e}")

        if not playlist_id:
            jarvis.say(f"No playlists found for genre: {genre}")
            return []

        try:
            tracks = sp.playlist_tracks(playlist_id, limit=limit)
        except Exception as e:
            jarvis.say(f"Error occurred while fetching playlist tracks: {e}")
            return []

        top_tracks = []
        for item in tracks['items']:
            track = item['track']
            if track:
                track_info = {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
                    'album': track['album']['name'] if track['album'] else 'Unknown Album'
                }
                top_tracks.append(track_info)

        return top_tracks