# jarviscli/tests/test_translate_plugin.py
import asyncio
import io
from contextlib import redirect_stdout
from unittest import TestCase, mock

# Import the async worker directly so we can bypass interactive prompts
from jarviscli.plugins.translate import performTranslation


class DummyJarvis:
    """
    Minimal Jarvis stub:
    - say(): collect messages (not strictly needed here, but handy)
    - input(): return scripted replies so we can answer "no" to save prompts
    """
    def __init__(self, scripted_inputs=None):
        self.scripted_inputs = list(scripted_inputs or [])
        self.said = []

    def say(self, msg, color=None):
        self.said.append(str(msg))

    def input(self):
        # Return next scripted input or default "no" to avoid file writes
        return self.scripted_inputs.pop(0) if self.scripted_inputs else "no"


class _FakeResult:
    """Mimics googletrans result object attributes used by the plugin."""
    def __init__(self, origin, text, src="auto", dest="en", pronunciation=""):
        self.origin = origin
        self.text = text
        self.src = src
        self.dest = dest
        self.pronunciation = pronunciation


class TestTranslatePlugin(TestCase):
    @mock.patch("jarviscli.plugins.translate.Translator")
    def test_auto_detect_single_line(self, MockTranslator):
        """
        Given src='auto' and a single-line text, the plugin should:
          - call Translator.translate once with our text
          - print a formatted single-line result (we capture stdout)
          - ask whether to save and we answer 'no' (no file created)
        """
        # Arrange fake translator as async context manager
        async def _fake_translate(text, src=None, dest=None):
            # Return a fake result where text becomes uppercased (easy to assert)
            return _FakeResult(origin=text, text=text.upper(), src=src or "auto", dest=dest or "en")

        class _AsyncMgr:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc, tb): return False
            # emulate the real method signature used by the plugin
            translate = staticmethod(_fake_translate)

        MockTranslator.return_value = _AsyncMgr()

        jarv = DummyJarvis(scripted_inputs=["no"])  # answer "no" to save prompt
        buf = io.StringIO()

        # Act
        with redirect_stdout(buf):
            asyncio.run(performTranslation(jarv, srcs="auto", des="english", tex="bonjour"))

        out = buf.getvalue()

        # Assert: the printed block should include origin and transformed text
        self.assertIn("[auto] bonjour", out.lower())    # src is printed
        self.assertIn("->", out)
        self.assertIn("BONJOUR".upper(), out)           # our fake returns uppercase

        # Ensure our stub jarvis captured the save prompt text call
        self.assertTrue(any("save" in s.lower() for s in jarv.said))

    @mock.patch("jarviscli.plugins.translate.Translator")
    def test_multiline_order_preserved(self, MockTranslator):
        """
        For multi-line input, each line is translated independently and
        output order is preserved.
        """
        lines = ["hola", "bonjour", "", "ciao"]  # include a blank line to ensure it’s preserved

        async def _fake_translate(text, src=None, dest=None):
            # tag each line deterministically so we can check order
            return _FakeResult(origin=text, text=f"[T]{text}")

        class _AsyncMgr:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc, tb): return False
            translate = staticmethod(_fake_translate)

        MockTranslator.return_value = _AsyncMgr()

        jarv = DummyJarvis(scripted_inputs=["no"])  # no saving
        buf = io.StringIO()

        with redirect_stdout(buf):
            asyncio.run(performTranslation(jarv, srcs="spanish", des="english", tex="\n".join(lines)))

        out = buf.getvalue().strip().splitlines()

        # Expected: translated lines with the blank line preserved as blank
        expected = ["[T]hola", "[T]bonjour", "[T]ciao"]
        # Filter out blank lines from output for comparison, but ensure there was a blank line
        self.assertIn("", buf.getvalue().splitlines(), "Blank line should be preserved")
        self.assertEqual([l for l in out if l != ""], expected)
