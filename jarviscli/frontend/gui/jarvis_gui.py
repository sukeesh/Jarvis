class JarvisGui():
    def __init__(self, jarvis):
        from frontend.gui.application import JarvisApp

        self.jarvis = jarvis
        self.app = JarvisApp(jarvis)
        self.app.run()

    def say(self, text, color=""):
        self.app.say(text)

    def show_prompt(self):
        # TODO
        pass

    def input(self, prompt="", color=""):
        return ''

    def exit(self):
        pass
