from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from ui.gui.screen_prompt import PromptScreen

Builder.load_file('ui/gui/screen_prompt.kv')


class GuiIO():
    def __init__(self, app):
        self.app = app

    def say(self, text, color=""):
        self.app.say(text)

    def input(self, prompt="", color=""):
        return ''

    def exit(self):
        pass


class JarvisApp(App):
    def __init__(self, jarvis):
        super().__init__()
        self.jarvis = jarvis
        self.api_io = GuiIO(self)
        self.jarvis.register_io(self.api_io)

    def build(self):
        self.screen_manager = ScreenManager()

        self.prompt_screen = PromptScreen(self.jarvis, name='Prompt')
        self.screen_manager.add_widget(self.prompt_screen)

        self.screen_manager.current = 'Prompt'
        return self.screen_manager

    def say(self, text):
        self.prompt_screen.impl.say(text)
