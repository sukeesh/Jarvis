import unittest
from tests import PluginTest
from plugins import voice
from CmdInterpreter import JarvisAPI
from Jarvis import Jarvis

# this test class contains test cases for the plugins "gtts" and "disable_gtts"
# which are included in the "voice.py" file in the "plugins" folder

class VoiceTest(PluginTest):

    # test "gtts" plugin
    def setUp(self):
        self.test_gtts = self.load_plugin(voice.gtts)

    def test_gtts(self):
        # run "gtts" plugin code
        self.test_gtts.run(voice.gtts)

        # verify that "gtts" plugin code works
        self.assertEqual(self.jarvis_api.get_data('gtts_status'), True)


    # test "disable_gtts" plugin
    def setUp(self):
        self.test_disable_gtts = self.load_plugin(voice.disable_gtts)

    def test_disable_gtts(self):
        # run "disable_gtts" plugin code
        self.test_disable_gtts.run(voice.disable_gtts)

        # verify that "disable_gtts" plugin code works
        self.assertEqual(self.jarvis_api.get_data('gtts_status'), False)

if __name__ == '__main__':
    unittest.main()
