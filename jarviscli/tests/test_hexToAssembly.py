import unittest
from tests import PluginTest
from plugins.mips_conv import MipsConverter


class TestMipsConverter(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(MipsConverter)


if __name__ == "__main__":
    unittest.main()
