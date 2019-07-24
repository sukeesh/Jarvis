import os

from plugin import plugin, require, LINUX


@plugin('shutdown')
def shutdown(jarvis, s):
    """Shutdown the system"""
    if s == '':
        s = jarvis.input('In how many minutes?: ')
    if s == '-c':
        os.system('sudo shutdown -c')
        return
    string = 'sudo shutdown -t ' + str(s)
    os.system(string)


@plugin('cancel shutdown')
def cancel_shutdown(jarvis, s):
    """Cancel an active shutdown"""
    os.system('sudo shutdown -c')
    jarvis.say('Shutdown cancelled.')


@plugin('reboot')
def reboot(jarvis, s):
    """Reboot the system"""
    if s == '':
        s = jarvis.input('In how many minutes?: ')
    string = 'sudo shutdown -r -t ' + str(s)
    os.system(string)


@require(native="systemctl", platform=LINUX)
@plugin('suspend')
def suspend(jarvis, s):
    """
    Suspend (to RAM) - also known as Stand By or Sleep mode.

    Operate PC on a minimum to save power but quickly wake up.
    """
    os.system('sudo systemctl suspend')


@require(native="systemctl", platform=LINUX)
@plugin('hibernate')
def hibernate(jarvis, s):
    """
    Hibernate - also known as "Suspend to Disk"

    Saves everything running to disk and performs shutdown.
    Next reboot computer will restore everything - including
    Programs and open files like the shutdown never happened.
    """
    os.system('sudo systemctl hibernate')


@require(native="systemctl", platform=LINUX)
@plugin('hybridsleep')
def hybridsleep(jarvis, s):
    """
    Hybrid sleep.
    Will quickly wake up but also survive power cut.
    Performs both suspend AND hibernate.
    Will quickly wake up but also survive power cut.
    """
    os.system("sudo systemctl hybrid-sleep")
