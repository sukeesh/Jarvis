import unittest
from plugins.lyrics import lyrics

from tests import PluginTest

# TODO: add tests for PyLyricsClone


class Lyrics_Test(PluginTest):

    def setUp(self):
        self.song_name = "everybody dies"
        self.artist_name = "ayreon"
        self.complete_info = "everybody dies-ayreon"
        self.wrong_info = "everybody dies-arebon"
        self.module = self.load_plugin(lyrics)

    def test_lyrics_found_given_full_parameters(self):
        self.assertIsNotNone(self.module.find(self.complete_info))

    def test_lyrics_not_found_given_incomplete_parameter(self):
        self.assertEqual(self.module.find(self.song_name),
                         "you forgot to add either song name or artist name")

    def test_lyrics_not_found_given_wrong_parameter(self):
        self.assertEqual(
            self.module.find(
                self.wrong_info),
            "Song or Singer does not exist or the API does not have lyrics")

    def test_split_works(self):
        self.assertEqual(self.module.parse(self.complete_info), [
            "everybody dies", "ayreon"])


if __name__ == '__main__':
    unittest.main()
