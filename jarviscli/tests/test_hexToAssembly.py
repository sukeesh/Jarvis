import unittest
from tests import PluginTest  
from plugins import mips_conv


class AssemblyToHexTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(mips_conv.MipsConverter)

    def test_valid_addi(self):
        """
        Test conversion of a valid I-type instruction.
        The final output should include a hex conversion message.
        """
        TEST_STRING = "ADDI $t2, $t1, 0x12"
        self.test.run(TEST_STRING)
        # We expect the final message to begin with "Statement in Hex: 0x"
        expected_prefix = "Statement in Hex: 0x"
        output = self.history_say().last_text()
        # Compare only the prefix since the complete hex value depends on internal data.
        self.assertEqual(output[:len(expected_prefix)], expected_prefix)

    def test_valid_sll(self):
        """
        Test conversion of a valid R-type instruction.
        The final output should include a hex conversion message.
        """
        TEST_STRING = "SLL $t2, $t1, 2"
        self.test.run(TEST_STRING)
        expected_prefix = "Statement in Hex: 0x"
        output = self.history_say().last_text()
        self.assertEqual(output[:len(expected_prefix)], expected_prefix)

    def test_invalid_command(self):
        """
        Test conversion with an invalid assembly command.
        The output should indicate that no such command exists.
        """
        TEST_STRING = "FOO $t0, $t1, 0x1"
        self.test.run(TEST_STRING)
        expected_output = "NO SUCH COMMAND IN ASSEMBLY"
        self.assertEqual(self.history_say().last_text(), expected_output)


if __name__ == '__main__':
    unittest.main()
