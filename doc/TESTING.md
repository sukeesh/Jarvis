# How to create tests

## Test plugins

Use this as a macro (replace XXX with the module you want to test):

```
import unittest
from tests import PluginTest  
from plugins import XXX


class XXXTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(XXX.XXX)

    def test_TESTCASE_1(self):
        # run code
        self.test.run(TEST_STRING)
         
        # verify that code works
        self.assertEqual(self.history_say.last_text, EXPECTED_OUTPUT)


if __name__ == '__main__':
    unittest.main()
```

Create a new file in jarviscli/tests/.

## PluginTest help functionality

Look [here](TEST_API.md).
