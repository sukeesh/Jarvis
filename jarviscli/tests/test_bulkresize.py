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
        valid_test_dir = os.path.join(DATA_PATH, 'images')
        actual = bulkresize.valid_path(valid_test_dir)
        self.assertTrue(actual)

    def test_invalid_path(self):
        invalid_test_dir = os.path.join(DATA_PATH, 'test_invalid_dir')
        actual = bulkresize.valid_path(invalid_test_dir)
        self.assertFalse(actual)

    def test_dir_exist(self):
        dir_exist = os.path.join(DATA_PATH, 'images')
        actual = bulkresize.dir_exist(dir_exist)
        self.assertTrue(actual)

    def test_dir_not_exist(self):
        dir_not_exist = os.path.join(DATA_PATH, 'test_invalid_dir')
        actual = bulkresize.dir_exist(dir_not_exist)
        self.assertFalse(actual)

    def test_list_contents(self):
        expected_list = [DATA_PATH + 'images/' + 'dummy-man.jpg']
        test_path = os.path.join(DATA_PATH, 'images')
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

    def test_rename_img(self):
        num = 1
        test_path = 'jarvis/jarviscli/plugins'
        expected = 'jarvis/jarviscli/plugins/1.jpg'
        actual = bulkresize.rename_img(test_path, num)
        self.assertEqual(actual, expected)

    def test_output_path_concat(self):
        test_path = 'jarvis/jarviscli/plugins'
        test_image_name = 'image.jpg'
        expected = 'jarvis/jarviscli/plugins/image.jpg'
        actual = bulkresize.output_path_concat(test_path, test_image_name)
        self.assertEqual(actual, expected)

    def test_get_extension_true(self):
        test_path = 'jarvis/jarviscli/plugins/image.jpg'
        actual = bulkresize.get_extension(test_path)
        self.assertTrue(actual)

    def test_get_extension_false(self):
        test_path = 'jarvis/jarviscli/plugins/image.py'
        actual = bulkresize.get_extension(test_path)
        self.assertFalse(actual)

    def test_spin(self):
        self.queue_input(DATA_PATH + 'images/')
        self.queue_input('y')
        self.queue_input(DATA_PATH + 'images/')
        self.queue_input('200')
        self.bulkresize_module.run(' ')
        actual = self.history_say().last_text()
        expected = 'Resizing Completed!! Thank you for using jarvis'
        self.assertEqual(actual, expected)
        os.remove(DATA_PATH + 'images/0.jpg')


if __name__ == '__main__':
    unittest.main()
