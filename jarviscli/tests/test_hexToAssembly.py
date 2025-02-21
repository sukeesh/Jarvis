import unittest
from tests import PluginTest
from plugins.mips_conv import MipsConverter


class TestMipsConverter(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(MipsConverter)


    def test_hex_to_assembly(self):
        """
        For Hex to Assembly:
            mips XXXXXXXX
            The above command calls mips with a 8 digit Hex code
            which makes a 32 bit instruction where the X are the
            Hex digits.

        Example run:
        ```
        mips 212A0012
        ADDI $t2 $t1 0x0012
        ```
        """
        self.test.run("212A0012")
        self.assertIn("ADDI $t2 $t1 0x0012", self.history_say().last_text())

    def test_no_command_exists(self):
        """Test that invalid hex commands are properly handled"""
        self.test.run("FFFFFFFF")
        self.assertIn("No such command exists", self.history_say().last_text())

if __name__ == "__main__":
    unittest.main()
