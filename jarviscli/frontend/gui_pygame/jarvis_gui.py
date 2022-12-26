from plugin import require
import threading


@require(imports=["pygame"])
class JarvisGui():
    QUALITY = 1

    def __init__(self, jarvis):
        print('!!!!')
        from frontend.gui_pygame.windowClass import JarvisWindow

        self.jarvis = jarvis
        self.jarvis_window = JarvisWindow(self.jarvis)

    def start(self):
        threading.Thread(target=self.jarvis_window.execute).start()

    def get_name():
        return 'GUI Frontend Pygame'

    def say(self, text, color=""):
        self.app.say(text)

    def show_prompt(self):
        # TODO
        pass

    def input(self, prompt="", color=""):
        return ''

    def exit(self):
        pass
