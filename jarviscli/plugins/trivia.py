import requests

from plugin import plugin, require


@require(network=True)
@plugin('trivia')
class trivia:
    errCode = "An error occurred. Please try again later."
    """
    Usage: Type trivia and follow the instructions.
    This plugin gives you trivia questions (mcq or true/false)
    for you to test your trivia knowledge
    """

    def __call__(self, jarvis, s):
        trivia_fetch = self.get_trivia(jarvis)
        question_type = trivia_fetch["results"][0]["type"]
        options = trivia_fetch["results"][0]["incorrect_answers"]
        if trivia_fetch is not None:
            if(question_type == "multiple"):
                self.mcq_question(jarvis, trivia_fetch)
            else:
                self.true_false_question(jarvis, trivia_fetch)

    def get_trivia(self, jarvis):
        """
        function creates request to api and fetches the corresponding data
        """
        url = "https://opentdb.com/api.php?amount=1"
        r = requests.get(url)
        return r.json()

    def true_false_question(self, jarvis, trivia_fetch):
        response_code = trivia_fetch["response_code"]
        if (response_code != 0):
            jarvis.say(response_code)
            return
        else:
            question = trivia_fetch["results"][0]["question"]
            question = question.replace("&quot;", "\"")
            jarvis.say("True/False: " + question)
            options = ["true", "false"]
            correct = trivia_fetch["results"][0]["correct_answer"]
            correct = correct.lower()
            self.true_false_answer(jarvis, options, correct)

    def true_false_answer(self, jarvis, options, correctAnswer):
        answerPrompt = "Please enter either \'true\' or \'false\'"
        answer = (jarvis.input(answerPrompt + "\n")).lower()
        while answer not in options:
            jarvis.say("Invalid option")
            answer = (jarvis.input(answerPrompt + "\n")).lower()
        if (answer == correctAnswer):
            jarvis.say("Correct!!")
        else:
            jarvis.say("Sorry, that's incorrect")

    def mcq_question(self, jarvis, trivia_fetch):
        response_code = trivia_fetch["response_code"]
        if (response_code != 0):
            jarvis.say(response_code)
            return
        else:
            question = trivia_fetch["results"][0]["question"]
            question = question.replace("&quot;", "\"")
            question = question.replace('&#039;', "'")
            jarvis.say("Multiple Choice: " + question)
            options = trivia_fetch["results"][0]["incorrect_answers"]
            correct_answer = trivia_fetch["results"][0]["correct_answer"]
            options.append(correct_answer)
            options.sort()
            option_count = 0
            answersDict = {}
            for option in options:
                option_count = option_count + 1
                answersDict[str(option_count)] = option
                jarvis.say(str(option_count) + ". " + option)
            self.mcq_answer(jarvis, answersDict, correct_answer, option_count)
        return

    def mcq_answer(self, jarvis, answersDict, correctAnswer, maxCount):
        answerPrompt = "Please enter an integer 1-" + str(maxCount)
        answer = jarvis.input(answerPrompt + "\n")
        while answer not in answersDict.keys():
            jarvis.say("Invalid option")
            answer = jarvis.input(answerPrompt + "\n")
        userAnswer = answersDict[answer]
        if (userAnswer == correctAnswer):
            jarvis.say("Correct!!")
        else:
            jarvis.say("Sorry, the correct answer was " + correctAnswer)
