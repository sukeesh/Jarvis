class Jarvis:
    def __init__(self):
        self.actions = {"how are you": "trash_talk",
                        "weather": "weather",
                        "open camera": "cheese",
                        }

    def actions(self, key):
        def trash_talk():
            pass
        def weather():
            pass
        def cheese():
            pass
        locals()[key]()

    def user_input(self):
        pass

    def executor(self):
        pass
