import unittest
import os
from tests import PluginTest
from plugins.hash import hash_data


class HashDataTest(PluginTest):
    """
    Tests For Hash Data Plugin
    Created with help from ChatGPT
    """

    def setUp(self):
        self.test = self.load_plugin(hash_data)

    def test_invalid_input_type(self):
        # Set predefined input values
        self.queue_input('s')
        self.queue_input('md5')
        self.queue_input('Hello, World!')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = "Invalid input type. Please enter "\
            "'string' or 'file'."
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_invalid_hash_function(self):
        # Set predefined input values
        self.queue_input('string')
        self.queue_input('m12')
        self.queue_input('Hello, World!')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = "Invalid hash function: m12"
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_hash_string1(self):
        # Set predefined input values
        self.queue_input('string')
        self.queue_input('md5')
        self.queue_input('Hello, World!')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: 65a8e27d8879283831b664bd8b7f0ad4'
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_hash_string2(self):
        # Set predefined input values
        self.queue_input('string')
        self.queue_input('sha256')
        self.queue_input('I love programming!')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: '\
            '005ab62754e4c38100017e5a515e1fd7e7072343a496669aa40c59367361a42e'
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_hash_string3(self):
        # Set predefined input values
        self.queue_input('string')
        self.queue_input('sha1')
        self.queue_input('Jarvis is the best.')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: 6951d3ce42ba70364'\
            '585925b40c1ea55bcd23e2a'
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_hash_file_invalid_path_md5(self):
        # Set predefined input values
        self.queue_input('file')
        self.queue_input('md5')
        self.queue_input('nonexistent_file.txt')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: Error: File not found '\
            'or inaccessible.'
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_hash_file_invalid_path_md5(self):
        # Set predefined input values
        self.queue_input('file')
        self.queue_input('sha1')
        self.queue_input('nonexistent_file.txt')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: Error: File not found '\
            'or inaccessible.'
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_hash_file_invalid_path_sha256(self):
        # Set predefined input values
        self.queue_input('file')
        self.queue_input('sha256')
        self.queue_input('nonexistent_file.txt')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: Error: File not found '\
            'or inaccessible.'
        self.assertEqual(self.history_say().last_text(), expected_output)

    def test_hash_file_valid_path1(self):
        # Create a temporary test file
        with open("test_file.txt", "w") as file:
            file.write("This is a test file.")

        # Set predefined input values
        self.queue_input('file')
        self.queue_input('md5')
        self.queue_input('test_file.txt')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: 3de8f8b0dc94b8c2230fab9ec0ba0506'
        self.assertEqual(self.history_say().last_text(), expected_output)

        # Clean up created file
        if os.path.isfile('test_file.txt'):
            os.remove('test_file.txt')

    def test_hash_file_valid_path2(self):
        # Create a temporary test file
        with open("test_file_2.txt", "w") as file:
            file.write("This is another test file.")

        # Set predefined input values
        self.queue_input('file')
        self.queue_input('sha1')
        self.queue_input('test_file_2.txt')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: dd6fdaba4cff3db969'\
            '2d2a86b39a331ad92c0667'
        self.assertEqual(self.history_say().last_text(), expected_output)

        # Clean up created file
        if os.path.isfile('test_file_2.txt'):
            os.remove('test_file_2.txt')

    def test_hash_file_valid_path3(self):
        # Create a temporary test file
        with open("test_file_3.txt", "w") as file:
            file.write("This is yet another test file.")

        # Set predefined input values
        self.queue_input('file')
        self.queue_input('sha256')
        self.queue_input('test_file_3.txt')

        # Run the plugin method
        self.test(self.jarvis_api, "")

        # Check the output
        expected_output = 'Hashed result: efa343369047cf2617265c74e92'\
            '911883efb70849db7a4194021608450eaee4d'
        self.assertEqual(self.history_say().last_text(), expected_output)

        # Clean up created file
        if os.path.isfile('test_file_3.txt'):
            os.remove('test_file_3.txt')


if __name__ == '__main__':
    unittest.main()
