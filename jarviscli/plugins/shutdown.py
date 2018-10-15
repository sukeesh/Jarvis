import os

from plugin import plugin


@plugin()
def shutdown(jarvis, s):
    """Shutdown the system"""
    if s == '':
        s = input('In how many minutes?: ')
    if s == '-c':
        os.system('sudo shutdown -c')
        return
    string = 'sudo shutdown -t ' + str(s)
    os.system(string)


@plugin()
def cancel_shutdown(jarvis, s):
    """Cancel an active shutdown"""
    os.system('sudo shutdown -c')
    jarvis.say('Shutdown cancelled.')


@plugin()
def reboot(jarvis, s):
    """Reboot the system"""
    if s == '':
        s = input('In how many minutes?: ')
    string = 'sudo shutdown -r -t ' + str(s)
    os.system(string)


@plugin(native="systemctl")
def suspend(jarvis, s):
    """
    Suspend (to RAM) - also known as Stand By or Sleep mode.

    Operate PC on a minimum to save power but quickly wake up.
    """
    os.system('sudo systemctl suspend')


@plugin(native="systemctl")
def hibernate(jarvis, s):
    """
    Hibernate - also known as "Suspend to Disk"

    Saves everything running to disk and performs shutdown.
    Next reboot computer will restore everything - including
    Programs and open files like the shutdown never happened.
    """
    os.system('sudo systemctl hibernate')


@plugin(native="systemctl")
def hybridsleep(jarvis, s):
    """
    Hybrid sleep.
    Will quickly wake up but also survive power cut.
    Performs both suspend AND hibernate.
    Will quickly wake up but also survive power cut.
    """
    os.system("sudo systemctl hybrid-sleep")
