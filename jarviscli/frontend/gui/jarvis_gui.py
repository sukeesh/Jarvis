class JarvisGui():
    QUALITY = 1

    def __init__(self, jarvis):
        from frontend.gui.application import JarvisApp

        self.jarvis = jarvis
        self.app = JarvisApp(jarvis)
        self.app.run()

    def get_name():
        return 'GUI Frontend'

    def say(self, text, color=""):
        self.app.say(text)

    def show_prompt(self):
        # TODO
        pass

    def input(self, prompt="", color=""):
        return ''

    def exit(self):
        pass
