import unittest

import youtube_search
import youtubesearchpython
from plugins import youtube
from tests import PluginTest
from youtubesearchpython import (
    ChannelSearch,
    ChannelsSearch,
    CustomSearch,
    Search,
    Video,
    VideoSortOrder,
)


class YouTubeTest(PluginTest):
    def setUp(self):
        self.youtube = self.load_plugin(youtube.youtube)

    def test_viewCount_one(self):
        test_input = "hello"
        expected_output = "Adele - Hello (Official Music Video)"

        customSearch = CustomSearch(test_input, VideoSortOrder.view, limit=1)
        latest_video = customSearch.result()
        returned_output = latest_video["result"][0]["title"]
        self.assertEqual(returned_output, expected_output)

    def test_viewCount_two(self):
        test_input = "messi"
        expected_output = "Rare Messi Moments"

        customSearch = CustomSearch(test_input, VideoSortOrder.view, limit=1)
        latest_video = customSearch.result()
        returned_output = latest_video["result"][0]["title"]
        self.assertEqual(returned_output, expected_output)

    def channel_info_test(self):
        test_input = "Marques Brownlee"
        expected_output = "https://www.youtube.com/@mkbhd"

        channelsSearch = ChannelsSearch(test_input, limit=1)
        channelsSearch_content = channelsSearch.result()
        returned_output = channelsSearch_content["result"][0]["link"]
        self.assertEqual(self.history_say().last_text(), expected_output)


if __name__ == "__main__":
    unittest.main()
