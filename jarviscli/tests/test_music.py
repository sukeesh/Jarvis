import unittest
import os
from mock import call, patch
from plugins import music
from CmdInterpreter import JarvisAPI

from tests import PluginTest, MockHistoryBuilder


class MusicTest(PluginTest):

    def setUp(self):
        self.music = self.load_plugin(music.play)
        self.song_name = 'torero chayanne'

    def test_song_is_searched_with_the_given_song_name(self):
        first_popen_call = call("ls music -tc")
        first_system_call = call(
            "cd music && instantmusic -s '"
            + self.song_name
            + "' 2> /dev/null")
        with patch.object(os, 'system', return_value=None) as mock_system:
            with patch.object(os, 'popen', return_value=os.popen("")) as mock_popen:
                self.music.run(self.song_name)
                mock_popen.assert_has_calls([first_popen_call])
                mock_system.assert_has_calls([first_system_call])

    def test_song_is_not_searched_without_a_song_name(self):
        with patch.object(os, 'system', return_value=None) as mock_system:
            with patch.object(os, 'popen', return_value=os.popen("")) as mock_popen:
                self.music.run('')
                self.assertFalse(mock_popen.called)
                self.assertFalse(mock_system.called)


if __name__ == '__main__':
    unittest.main()
