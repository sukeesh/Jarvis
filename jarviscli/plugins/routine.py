from plugin import plugin


ROUTINES = "routines"


def create_routine(jarvis, commands, name):
    """
    Saves a new routine to memory with a name and a list of instructions.
    :return: Nothing to return.
    """
    routines = jarvis.get_data(ROUTINES)
    if routines is None:
        jarvis.add_data(ROUTINES, {name: commands})
    else:
        routines[name] = commands
        jarvis.update_data(ROUTINES, routines)


def execute_routine(jarvis, name):
    """
    Executes a routine saved in memory based on its name. If the routine doesn't exist, returns False.

    :return: Whether or not the requested routine exists.
    """
    routines = jarvis.get_data(ROUTINES)
    try:
        routine = routines[name]
    except (TypeError, KeyError) as e:
        return False
    for command in routine:
        jarvis.eval(command)
    return True


@plugin("create routine")
def new_routine(jarvis, s):
    if s == "":
        jarvis.say("You forgot to give a name.")
        return
    commands = []
    while True:
        jarvis.say("Type a command, or press enter to finish the routine.")
        command = jarvis.input()
        if command == "":
            break
        commands.append(command)
    create_routine(jarvis, commands, s)


@plugin("call routine")
def call_routine(jarvis, s):
    success = execute_routine(jarvis, s)
    if not success:
        jarvis.say("The routine you requested doesn't seem to exist.")


@plugin("list routines")
def list_routines(jarvis, s):
    routines = jarvis.get_data(ROUTINES)
    for i in routines.keys():
        jarvis.say(str(i))


@plugin("delete routine")
def delete_routines(jarvis, s):
    routines = jarvis.get_data(ROUTINES)
    if s in routines:
        routines.pop(s)
        jarvis.update_data(ROUTINES, routines)
    else:
        jarvis.say("Invalid routine name")
