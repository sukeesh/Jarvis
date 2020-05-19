import unittest
from unittest import mock
from tests import PluginTest
from plugins import create_plugin


class create_pluginTest(PluginTest):

    def test_format_filename(self):
        actual = create_plugin.format_filename("my test!@#")
        expected = "my_test"
        self.assertEquals(actual, expected)

    def test_file_exists_True(self):
        actual = create_plugin.file_exists("test")
        self.assertTrue(actual)

    def test_file_exists_False(self):
        actual = create_plugin.file_exists("ghost")
        self.assertFalse(actual)


if __name__ == '__main__':
    unittest.main()
