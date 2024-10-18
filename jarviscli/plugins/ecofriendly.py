from plugin import plugin
from colorama import Fore


@plugin('ecofriendly')
class Ecofriendly:
    QUESTIONS = [
        "Do you regularly reduce your water consumption?",
        "Do you turn off lights and electronic devices when you're not using them?",
        "Do you buy products in bulk or with minimal packaging?",
        "Do you try to buy local and seasonal products?",
        "Do you often use sustainable transportation (walking, cycling, public transportation)?",
        "Do you systematically recycle household waste?",
        "Do you compost food scraps or organic waste?",
        "Have you reduced your meat consumption?",
        "Do you avoid plastic bottles and prefer reusable water bottles?",
        "Do you participate in environmental actions in your community?"
    ]

    def __call__(self, jarvis, s):
        self.intro(jarvis)
        score = self.ask_questions(jarvis)
        self.display_score(jarvis, score)

    def intro(self, jarvis):
        jarvis.say("Welcome to the Eco Habits Quiz!", Fore.BLUE)
        jarvis.say("You'll be asked a series of simple yes/no questions", Fore.BLUE)
        jarvis.say("to assess how eco-friendly your daily habits are.", Fore.BLUE)
        jarvis.say("Please answer with 'y' for yes or 'n' for no.", Fore.BLUE)

    def ask_questions(self, jarvis):
        score = 0
        for question in self.QUESTIONS:
            jarvis.say(question)
            response = input().lower().strip()
            if response == 'y':
                score += 1
            elif response != 'n':
                jarvis.say("Please answer with 'y' or 'n'.", Fore.RED)
        return score

    def display_score(self, jarvis, score):
        if score <= 3:
            jarvis.say("\nProfile: Beginner", Fore.RED)
            jarvis.say("Tips: Start with small actions like turning off lights and avoiding single-use plastic.", Fore.GREEN)
        elif score <= 7:
            jarvis.say("\nProfile: Moderate Eco-Friendly", Fore.CYAN)
            jarvis.say("Tips: Explore new ways to reduce your carbon footprint, such as composting your waste.", Fore.GREEN)
        else:
            jarvis.say("\nProfile: Eco-Engaged", Fore.YELLOW)
            jarvis.say("Tips: Share your experience with others to inspire those around you to follow your example.", Fore.GREEN)

