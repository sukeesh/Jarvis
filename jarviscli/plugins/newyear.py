from jarviscli import entrypoint


@entrypoint
def newyear(jarvis, s):
    tree = "     *\n"\
           "    ###\n"\
           "   #####\n"\
           "    ###\n"\
           "   #####\n"\
           "  #######\n"\
           "   #####\n"\
           "  #######\n"\
           "    ###\n"\
           "    ###"
    jarvis.say(tree)
