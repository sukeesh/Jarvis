import unittest
from tests import PluginTest  
from plugins.morse_code import morse_code


class morse_codeTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(morse_code)

    # testind encode
    def test_TESTCASE_1(self):
        # run code
        choice = 1
        message = "hello world"
        result = self.test.run(choice, message)
         
        # verify that code works
        self.assertEqual(result, ".... . .-.. .-.. --- | .-- --- .-. .-.. -..")

    # testing decode
	def test_TESTCASE_2(self):
        # run code
        choice = 2
        message = ".. | .- -- | .--- .- .-. ...- .. ..."
        result = self.test.run(choice, message)
         
        # verify that code works
        self.assertEqual(result, "i am jarvis")


if __name__ == '__main__':
    unittest.main()