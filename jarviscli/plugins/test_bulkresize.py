from unittest import mock
import unittest
import os
from Jarvis import Jarvis
from plugins.bulkresize import spin
from plugins import bulkresize

from tests import PluginTest


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(CURRENT_PATH, '..', 'data/')


class Bulkresize(PluginTest):

    def setUp(self):
        self.bulkresize_module = self.load_plugin(spin)
    
    def test_valid_path(self):
        valid_test_dir = os.path.join(DATA_PATH, 'test_dir')
        actual = bulkresize.valid_path(valid_test_dir)
        self.assertTrue(actual)

    def test_invalid_path(self):
        invalid_test_dir = os.path.join(DATA_PATH, 'test_invalid_dir')
        actual = bulkresize.valid_path(invalid_test_dir)
        self.assertFalse(actual)

    def test_dir_exist(self):
        dir_exist = os.path.join(DATA_PATH, 'test_dir')
        actual = bulkresize.dir_exist(dir_exist)
        self.assertTrue(actual)

    def test_dir_not_exist(self):
        dir_not_exist = os.path.join(DATA_PATH, 'test_invalid_dir')
        actual = bulkresize.dir_exist(dir_not_exist)
        self.assertFalse(actual)

    def test_list_contents(self):
        expected_list = [DATA_PATH + 'test_dir/' + 'test.png']
        test_path = os.path.join(DATA_PATH, 'test_dir')
        actual = bulkresize.list_contents(test_path)
        self.assertListEqual(actual, expected_list)

    def test_remove_backslash(self):
        path_str = '/jarvis/jarviscli/plugin\\ name'
        expected = '/jarvis/jarviscli/plugin name'
        actual = bulkresize.remove_backslash(path_str)
        self.assertEqual(actual, expected)

    @unittest.mock.patch('os.makedirs')
    def test_create_dir(self, os_makedirs):
        path = os.path.join(DATA_PATH, 'dir_to_be_created')
        bulkresize.create_dir(path)
        os_makedirs.assert_called_once_with(path)


if __name__ == '__main__':
    unittest.main()