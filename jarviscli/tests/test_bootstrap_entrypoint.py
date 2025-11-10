# jarviscli/tests/test_bootstrap_entrypoint.py

import unittest
from unittest import mock
import importlib

class TestBootstrapEntrypoint(unittest.TestCase):
    def test_module_runs_cmdloop_via_start(self):
        # Import the entry module once so we can patch the Jarvis symbol it bound
        import jarviscli.__main__ as entry

        # Patch the Jarvis name inside the entry module to avoid heavy init/plugin loading
        with mock.patch("jarviscli.__main__.Jarvis") as MockJarvis:
            inst = MockJarvis.return_value
            # Call the CLI entrypoint
            entry.main()
            # Ensure the entrypoint delegates to Jarvis.start()
            inst.start.assert_called_once()

    def test_entry_exposes_main_callable(self):
        # Sanity: re-import to ensure module loads and exposes main()
        entry = importlib.import_module("jarviscli.__main__")
        self.assertTrue(callable(getattr(entry, "main", None)))
