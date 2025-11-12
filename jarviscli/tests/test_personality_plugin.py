# jarviscli/tests/test_personality_plugin.py
import sys, types, importlib
from unittest import TestCase, mock

def _identity_decorator(*dargs, **dkwargs):
    def _wrap(obj):
        return obj
    return _wrap

class TestPersonalityPlugin(TestCase):
    @mock.patch("webbrowser.open_new")  # patch global since we'll stub the module before import
    def test_quiz_outputs_type_and_url(self, mock_open):
        # Ensure we import the plugin with a no-op decorator
        sys.modules.pop("jarviscli.plugins.personality", None)
        # Provide a stub 'plugin' module so `from plugin import plugin` becomes a no-op
        sys.modules["plugin"] = types.SimpleNamespace(plugin=_identity_decorator)

        personality_mod = importlib.import_module("jarviscli.plugins.personality")
        personality_test = personality_mod.personality_test

        # Build deterministic answers -> INFJ
        answers = [3] * 32

        def set_indices(val, idxs):
            for i in idxs:
                answers[i - 1] = val

        # IE
        set_indices(1, (15, 23, 27))
        set_indices(5, (3, 7, 11, 19, 31))
        # SN
        set_indices(5, (4, 8, 12, 16, 20, 32))
        set_indices(1, (24, 28))
        # FT
        set_indices(1, (6, 10, 22))
        set_indices(5, (2, 14, 18, 26, 30))
        # JP
        set_indices(1, (1, 5, 13, 21, 29))
        set_indices(5, (9, 17, 25))

        inst = personality_test()
        inst.answers = {i + 1: val for i, val in enumerate(answers)}

        # Exercise the logic you fixed
        inst.get_scores()
        self.assertEqual(inst.type_str, "INFJ")

        inst.open_analysis()
        mock_open.assert_called_once_with(
            "https://www.16personalities.com/infj-personality"
        )
