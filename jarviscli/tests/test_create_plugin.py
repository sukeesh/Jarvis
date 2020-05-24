import unittest
from unittest import mock
from tests import PluginTest
from plugins import create_plugin
from plugins.create_plugin import create_plugin_MAC
from plugins.create_plugin import create_plugin_LINUX


class create_pluginTest(PluginTest):

    def setUp(self):
        self.mac_module = self.load_plugin(create_plugin_MAC)
        self.linux_module = self.load_plugin(create_plugin_LINUX)

    @unittest.mock.patch('os.system')
    def test_create_file_MAC(self, os_system):
        self.mac_module.run("my_test")
        output = self.history_say().last_text()
        # Pull the template from the main plugin
        template = create_plugin.create_template(create_plugin.CUSTOM_PLUGINS_PATH, "my_test")
        # Mock is called excactly once because the file was never created so it will not open
        os_system.assert_called_once_with(template)

    @unittest.mock.patch('os.system')
    def test_create_file_LINUX(self, os_system):
        self.linux_module.run("my_test")
        output = self.history_say().last_text()
        # Pull the template from the main plugin
        template = create_plugin.create_template(create_plugin.CUSTOM_PLUGINS_PATH, "my_test")
        # Mock is called excactly once because the file was never created so it will not open
        os_system.assert_called_once_with(template)

    def test_format_filename(self):
        actual = create_plugin.format_filename("my test!@#")
        expected = "my_test"
        self.assertEqual(actual, expected)

    def test_file_exists_True(self):
        actual = create_plugin.file_exists("test")
        self.assertTrue(actual)

    def test_file_exists_False(self):
        actual = create_plugin.file_exists("ghost")
        self.assertFalse(actual)


if __name__ == '__main__':
    unittest.main()
