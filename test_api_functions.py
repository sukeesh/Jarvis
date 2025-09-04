import unittest
from unittest.mock import patch
from chatgpt_api import generate_names_chat, draft_email_chat
from jarvis import process_jarvis_command


class TestJarvisFunctions(unittest.TestCase):

    # Test for generate_names_chat function
    @patch('chatgpt_api.generate_names_chat')
    def test_generate_names_chat(self, mock_generate_names_chat):
        mock_generate_names_chat.return_value = ["Seraphim Springs", "Celestial Heights"]

        theme = "magic city"
        names = generate_names_chat(theme)

        self.assertEqual(names, ["Seraphim Springs", "Celestial Heights"])
        mock_generate_names_chat.assert_called_with(theme)

    # Test for draft_email_chat function
    @patch('chatgpt_api.draft_email_chat')
    def test_draft_email_chat(self, mock_draft_email_chat):
        mock_draft_email_chat.return_value = "Subject: Senior Design\n\nHello Jesse,\n\nHere are the updates..."

        recipient = "Jesse"
        topic = "Senior Design"
        main_points = ["Agenda overview", "Team introductions", "Timeline discussion"]
        email = draft_email_chat(recipient, topic, main_points)

        self.assertIn("Agenda overview", email)
        self.assertIn("Team introductions", email)
        self.assertIn("Timeline discussion", email)
        mock_draft_email_chat.assert_called_with(recipient, topic, main_points)

    # Test for process_jarvis_command function - name generation
    @patch('pyttsx3.init')
    @patch('chatgpt_api.generate_names_chat')
    def test_process_jarvis_command_name(self, mock_generate_names_chat, mock_init):
        mock_engine = mock_init.return_value

        mock_generate_names_chat.return_value = ["Seraphim Springs", "Celestial Heights"]

        command = "Jarvis, give me names about magic city"
        process_jarvis_command(command)

        mock_generate_names_chat.assert_called_with("magic city")
        mock_engine.say.assert_any_call("Here are some names about magic city.")
        mock_engine.say.assert_any_call("Seraphim Springs")
        mock_engine.say.assert_any_call("Celestial Heights")

    # Test for process_jarvis_command function - email drafting
    @patch('pyttsx3.init')
    @patch('chatgpt_api.draft_email_chat')
    def test_process_jarvis_command_email(self, mock_draft_email_chat, mock_init):
        mock_engine = mock_init.return_value

        mock_draft_email_chat.return_value = "Subject: Senior Design\n\nHello Jesse,\n\nHere are the updates..."

        command = "Jarvis, draft an email"
        process_jarvis_command(command)

        mock_draft_email_chat.assert_called_with("Jesse", "Senior Design", ["Agenda overview", "Team introductions", "Timeline discussion"])
        mock_engine.say.assert_any_call("Here is your drafted email.")
        mock_engine.say.assert_any_call("Subject: Senior Design\n\nHello Jesse,\n\nHere are the updates...")

if __name__ == '__main__':
    unittest.main()
