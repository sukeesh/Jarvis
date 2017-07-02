import unittest
import os

from packages.memory.memory import Memory, module_path


class MemoryTest(unittest.TestCase):

    def test_memory(self):

        m = Memory('test-mem.json')
        m.add_data('test', 'test_data')

        self.assertEqual(str(m.get_data('test')), 'test_data')

    def tearDown(self):

        os.remove(os.path.join(module_path, 'test-mem.json'))


if __name__ == '__main__':
    unittest.main()
