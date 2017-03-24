import aiml

import os

module_path = os.path.dirname(__file__)


class Brain:

    def __init__(self):
        self.kernel = aiml.Kernel()
        self.kernel.verbose(False) # to remove all of the system loading output
        self.kernel.learn(os.path.join(module_path, 'chat.aiml'))


    def respond(self, text):
        return self.kernel.respond(text)


# Create the kernel and learn AIML files


# Press CTRL-C to break this loop
#while True:
#    print kernel.respond(raw_input("Enter your message >> "))
