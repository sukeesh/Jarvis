import os

from plugin import plugin


@plugin()
def shutdown(jarvis, s):
    """Shutdown the system."""
    minutes = input('In how many minutes?: ')
    string = 'sudo shutdown -t ' + str(minutes)
    os.system(string)


@plugin()
def cancel_shutdown(jarvis, s):
    """Cancel an active shutdown"""
    os.system('sudo shutdown -c')
    jarvis.say('Shutdown cancelled.')


@plugin()
def reboot(jarvis, s):
    """shutdown: cancel"""
    minutes = input('In how many minutes?: ')
    string = 'sudo shutdown -r -t ' + str(minutes)
    os.system(string)
