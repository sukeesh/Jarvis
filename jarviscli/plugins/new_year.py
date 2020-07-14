from plugin import plugin


@plugin("christmas-tree")
def new_year(jarvis, data):
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
