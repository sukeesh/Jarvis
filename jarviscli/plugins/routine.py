from plugin import plugin

@plugin("create routine")
def new_routine(jarvis, s):
    commands = []
    while True:
        jarvis.say("Type a command, or press enter to finish the routine")
        command = jarvis.input()
        if command == "":
            break
        commands.append(command)
    jarvis.create_routine(commands, s)

@plugin("call routine")
def call_routine(jarvis, s):
    success = jarvis.execute_routine(s)
    if not success:
        jarvis.say("The routine you requested doesn't seem to exist.")

@plugin("list routines")
def list_routines(jarvis, s):
    routines = jarvis.get_data("routines")
    for i in routines.keys():
        jarvis.say(str(i))

@plugin("delete routine")
def delete_routines(jarvis, s):
    routines = jarvis.get_data("routines")
    routines.pop(s)
    jarvis.update_data("routines", routines)
