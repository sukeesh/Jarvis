from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from frontend.gui.screen_prompt import PromptScreen

Builder.load_file('jarviscli/frontend/gui/screen_prompt.kv')


class JarvisApp(App):
    def __init__(self, jarvis):
        self.jarvis = jarvis
        super().__init__()

    def build(self):
        self.screen_manager = ScreenManager()

        self.prompt_screen = PromptScreen(self.jarvis, name='Prompt')
        self.screen_manager.add_widget(self.prompt_screen)

        self.screen_manager.current = 'Prompt'
        return self.screen_manager

    def say(self, text):
        self.prompt_screen.impl.say(text)
