import unittest
from unittest.mock import patch, Mock
import requests
from your_module import SoccerScores, JarvisAPI  # Adjust import according to your project structure

class TestSoccerScores(unittest.TestCase):
    def setUp(self):
        # Setup a mock for the JarvisAPI which would be passed to the plugin
        self.jarvis = Mock()
        self.jarvis.say = Mock()

        # Instantiate the SoccerScores class
        self.plugin = SoccerScores()

    @patch('requests.get')
    def test_successful_response(self, mock_get):
        # Mock the JSON response to simulate the API returning valid game data
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            "games": [
                {"strEvent": "Team A vs Team B", "dateEvent": "2024-04-16", "intHomeScore": "2", "intAwayScore": "1", "strStatus": "Finished"}
            ]
        }
        mock_get.return_value.raise_for_status = Mock()

        self.plugin.print_latest_scores(self.jarvis)
        self.jarvis.say.assert_any_call("Fetching the latest soccer scores...")
        self.jarvis.say.assert_any_call("Match: Team A vs Team B", color=Fore.BLUE)
        self.jarvis.say.assert_any_call("Score: 2 - 1", color=Fore.GREEN)

    @patch('requests.get')
    def test_no_games_found(self, mock_get):
        # Simulate the API returning valid response but no games
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"games": []}
        mock_get.return_value.raise_for_status = Mock()

        self.plugin.print_latest_scores(self.jarvis)
        self.jarvis.say.assert_called_with("No recent games data found.", color=Fore.RED)

    @patch('requests.get')
    def test_api_error(self, mock_get):
        # Simulate an API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        self.plugin.print_latest_scores(self.jarvis)
        self.jarvis.say.assert_called_with("An error occurred while fetching data: API Error", color=Fore.RED)

    @patch('requests.get')
    def test_invalid_json_response(self, mock_get):
        # Simulate invalid JSON response
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

        self.plugin.print_latest_scores(self.jarvis)
        self.jarvis.say.assert_called_with("An error occurred while fetching data: Invalid JSON", color=Fore.RED)

if __name__ == '__main__':
    unittest.main()
