import aiml

import os

# this sets the path to the modules directory not the directory it was call from
module_path = os.path.dirname(__file__)


class Brain:

    def __init__(self):
        self.kernel = aiml.Kernel()
        self.kernel.verbose(False)  # remove system output

        # brain file already exists load it
        if os.path.isfile(os.path.join(module_path, "bot_brain.brn")):
            self.kernel.bootstrap(brainFile=os.path.join(
                module_path, "bot_brain.brn"))
        # if brain file doesnt exist load std-startup.xml and create and save brain file
        else:
            self.create_brain()

    def respond(self, text):
        return self.kernel.respond(text)

    def create_brain(self):
        self.kernel.learn(os.path.join(module_path, "chat.aiml"))
        self.kernel.learn(os.path.join(module_path, "emotion.aiml"))

        # This file should go last. It contains wild cards
        self.kernel.learn(os.path.join(module_path, "default.aiml"))
        self.kernel.saveBrain(os.path.join(module_path, "bot_brain.brn"))

    def remove_brain(self):
        os.remove(os.path.join(module_path, "bot_brain.brn"))
