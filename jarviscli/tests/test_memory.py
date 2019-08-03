import unittest
import os

from packages.memory.memory import Memory, module_path


class MemoryTest(unittest.TestCase):
    def test_memory(self):

        m = Memory("test-mem.json")
        m.add_data("test", "test_data")
        self.assertEqual(m.get_data("test"), "test_data")

        m.update_data("test", "test_update")
        self.assertEqual(m.get_data("test"), "test_update")

        m.del_data("test")
        self.assertEqual(m.get_data("test"), None)

        m.add_data("test1", "test_data1")
        m.add_data("test2", "test_data2")

        self.assertEqual(m.get_all(), {"test1": "test_data1", "test2": "test_data2"})

    def tearDown(self):

        os.remove(os.path.join(module_path, "test-mem.json"))


if __name__ == "__main__":
    unittest.main()
