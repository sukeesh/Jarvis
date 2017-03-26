import aiml

import os

#this sets the path to the modules directory not the directory it was call from
module_path = os.path.dirname(__file__)


class Brain:

    def __init__(self):
        self.kernel = aiml.Kernel()
        #self.kernel.verbose(False) # rmove system output

        # brain file already exists load it
        if os.path.isfile(os.path.join(module_path,"bot_brain.brn")):
            self.kernel.bootstrap(brainFile = os.path.join(module_path, "bot_brain.brn"))
        # if brain file doesnt exist load std-startup.xml and create and save brain file
        else:
            self.kernel.bootstrap(learnFiles = os.path.join(module_path, "std-startup.xml"), commands = "load aiml b")
            self.kernel.saveBrain(os.path.join(module_path, "bot_brain.brn"))


    def respond(self, text):
        return self.kernel.respond(text)
