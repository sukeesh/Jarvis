import unittest
from unittest.mock import MagicMock, Mock, patch
from tests import PluginTest
from plugins.music_recognition import MusicRecognition
import requests

"""Instructions to run this test.

source env/bin/activate
cd jarviscli/
python -m unittest tests/test_music_recognition.py
"""


class MusicRecognitionTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(MusicRecognition)

    def tearDown(self):
        PluginTest.tearDown(self)

    def mock_list_microphones():
        return ['mock_mic']

    def mock_microphone(device_index):
        return MagicMock()

    def mock_record(source, duration):
        """
        Method used to mock the method record
        of speech_recognition to return a 15s
        excerpt of the Addams Family song
        """

        song = requests.get(
            'https://drive.google.com/uc?export=download&id=1LAM_dxzuGlrCehg4_wIf68Z_erNaMXGs',
            stream=True)
        if song.status_code == 200:
            mock_object = Mock()
            mock_object.get_wav_data.return_value = song.content
            return mock_object
        else:
            raise Exception("Could not download test music")

    @patch('speech_recognition.Microphone.list_microphone_names', side_effect=mock_list_microphones)
    @patch('speech_recognition.Microphone', side_effect=mock_microphone)
    @patch('speech_recognition.Recognizer.record', side_effect=mock_record)
    def test_music_recognition(self, args, args1, args2):
        """Test workflow to recognize a music."""

        # insert data to be retrieved by jarvis.input()
        self.queue_input('2')           # select 2 on the menu

        # microphone will not be detected...
        self.queue_input('1')           # select the mock_mic

        # Addams Family song will now be given to Shazam
        self.queue_input('2')           # send to recognize

        self.queue_input('4')           # leave after recording menu

        self.queue_input('q')           # leave program

        # run code
        self.test.run('')

        # verify that the mock mic was retrieved
        self.assertEqual(self.history_say().view(index=9)[0],
                         '1: mock_mic')

        # verify that the right song title was obtained
        self.assertEqual(self.history_say().view(index=18)[0],
                         'Song Title: The Addams Family')

        # verify that the right song artist was obtained
        self.assertEqual(self.history_say().view(index=19)[0],
                         'Song Artist: Andrew Gold')

        # verify that the client quited the menu
        self.assertEqual(self.history_say().last_text(),
                         'See you next time :D')


if __name__ == '__main__':
    unittest.main()
