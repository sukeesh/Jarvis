import unittest
from unittest import mock

# We need to import the actual function from your plugin file
# Make sure your plugin file is named 'wiki_summary.py'
import wiki_summary

# We need to simulate the exceptions from the wikipedia library
from wikipedia import exceptions


class TestWikiSummary(unittest.TestCase):

    def setUp(self):
        """This method runs before each test, setting up a fresh mock object."""
        self.mock_jarvis = mock.MagicMock()

    @mock.patch('wiki_summary.wikipedia')
    def test_successful_summary(self, mock_wiki_module):
        """Tests a successful Wikipedia lookup."""
        # 1. Configure the mock to return a specific summary
        expected_summary = "Python is a high-level programming language."
        mock_wiki_module.summary.return_value = expected_summary

        # 2. Call the plugin function with the mock jarvis and a search term
        wiki_summary.wiki(self.mock_jarvis, "python programming")

        # 3. Assert that jarvis.say() was called with our expected summary
        # We check the second call, because the first is "Searching..."
        self.mock_jarvis.say.call_args_list[1][0][0] == expected_summary

    @mock.patch('wiki_summary.wikipedia')
    def test_page_not_found(self, mock_wiki_module):
        """Tests the case where a Wikipedia page doesn't exist."""
        # 1. Configure the mock to raise a PageError exception
        search_term = "nonexistent page for testing"
        mock_wiki_module.summary.side_effect = exceptions.PageError(page_title=search_term)

        # 2. Call the plugin function
        wiki_summary.wiki(self.mock_jarvis, search_term)

        # 3. Assert that jarvis.say() was called with the correct error message
        expected_error_msg = f"Sorry, I could not find a Wikipedia page for '{search_term}'."
        self.mock_jarvis.say.assert_called_with(expected_error_msg, mock.ANY) # mock.ANY ignores the colorama argument

    @mock.patch('wiki_summary.wikipedia')
    def test_disambiguation_error(self, mock_wiki_module):
        """Tests a search for an ambiguous term."""
        # 1. Configure the mock to raise a DisambiguationError
        options = ["Java (island)", "Java (programming language)", "Java (coffee)"]
        mock_wiki_module.summary.side_effect = exceptions.DisambiguationError(title="java", options=options)

        # 2. Call the plugin function
        wiki_summary.wiki(self.mock_jarvis, "java")

        # 3. Assert that jarvis.say() was called with the list of options
        # We create a list of expected calls to check against
        expected_calls = [
            mock.call("Searching Wikipedia for 'java'...", mock.ANY),
            mock.call("'java' is ambiguous. Did you mean one of these?", mock.ANY),
            mock.call("1. Java (island)"),
            mock.call("2. Java (programming language)"),
            mock.call("3. Java (coffee)")
        ]
        self.mock_jarvis.say.assert_has_calls(expected_calls)

    def test_no_search_term_provided(self):
        """Tests the case where the user provides no input at all."""
        # 1. Configure the mock's input method to return an empty string
        self.mock_jarvis.input.return_value = ""

        # 2. Call the plugin with an empty string, simulating "wiki" with no args
        wiki_summary.wiki(self.mock_jarvis, "")

        # 3. Assert that the correct "no input" message was shown
        self.mock_jarvis.say.assert_called_with("No search term provided.", mock.ANY)


if __name__ == '__main__':
    unittest.main()