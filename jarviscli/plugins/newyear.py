from plugin import plugin


@plugin("christmas")
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
