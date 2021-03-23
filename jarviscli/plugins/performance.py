import os
from plugin import plugin, require, UNIX


@require(platform=UNIX)
@plugin("performance")
def performance_UNIX(jarvis, s):
    """
        Displays Hardware Performance using 'htop'
    """
    print('Getting info using \'htop\' .....')
    print('Might require your password')
    string = 'sudo htop'
    os.system(string)
