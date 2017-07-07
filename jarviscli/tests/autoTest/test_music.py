import unittest
import os
from mock import call, patch
from packages import music


class MusicTest(unittest.TestCase):

    def setUp(self):
        self.song_name = 'torero chayanne'

    def test_song_is_searched_with_the_given_song_name(self):
        first_popen_call = call("ls | grep -i " + '"' + self.song_name + '"')
        first_system_call = call(
            "instantmusic -s " + self.song_name + " 2> /dev/null")
        with patch.object(os, 'system', return_value=None) as mock_system:
            with patch.object(os, 'popen', return_value=os.popen("")) as mock_popen:
                music.play(self.song_name)
                mock_popen.assert_has_calls([first_popen_call])
                mock_system.assert_has_calls([first_system_call])

    def test_song_is_not_searched_without_a_song_name(self):
        with patch.object(os, 'system', return_value=None) as mock_system:
            with patch.object(os, 'popen', return_value=os.popen("")) as mock_popen:
                music.play('')
                self.assertFalse(mock_popen.called)
                self.assertFalse(mock_system.called)
