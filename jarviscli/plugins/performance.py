import os

from jarviscli import entrypoint


@entrypoint
def performance_UNIX(jarvis, s):
    """
        Displays Hardware Performance using 'htop'
    """
    print('Getting info using \'htop\' .....')
    print('Might require your password')
    string = 'sudo htop'
    os.system(string)
