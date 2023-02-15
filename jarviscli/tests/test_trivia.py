import unittest
from tests import PluginTest  
from plugins.trivia import trivia
import requests
from mock import patch, call

JSOn={"response_code":"1","results":[{"category":"General Knowledge","type":"multiple","difficulty":"easy","question":"What was the name of the WWF professional wrestling tag team made up of the wrestlers Ax and Smash?","correct_answer":"Demolition","incorrect_answers":["The Dream Team","The Bushwhackers","The British Bulldogs"]}]}

class TriviaTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(trivia)

    def test_Trivia_true_question(self):
        # run code
        self.test.true_false_question(self.jarvis_api,JSOn)
        # verify that code works
        self.assertEqual(self.history_say().last_text(), "1")


    def test_Trivia_true_answer(self):
        self.queue_input("true")
        self.test.true_false_answer(self.jarvis_api,["true","false"],JSOn["results"][0]["correct_answer"])
        self.assertEqual(self.history_say().last_text(), "Sorry, that's incorrect")


    def test_Trivia_mcq_question(self):
        # run code
        self.test.mcq_question(self.jarvis_api,JSOn)
        # verify that code works
        self.assertEqual(self.history_say().last_text(), "1")

    def test_Trivia_get(self):
        with patch.object(requests, 'get') as get_mock:
            self.test.get_trivia(self.jarvis_api)
            get_mock.assert_called_with(
                "https://opentdb.com/api.php?amount=1")

if __name__ == '__main__':
    unittest.main()
