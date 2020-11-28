from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen


class PromptScreen(Screen):
    def __init__(self, jarvis, **args):
        super().__init__(**args)
        self.jarvis = jarvis


class Prompt(BoxLayout):
    def press_ok(self):
        self.jarvis.execute_once(self.prompt_text.text)
        self.prompt_text.text = ''

    def say(self, text):
        self.output.text += text + '\n'
