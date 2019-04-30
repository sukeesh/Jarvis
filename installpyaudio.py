import distro
import os
import platform
import sys
from six.moves import input


install_command = None
if platform.system().lower() == "linux":
    pm = {
        'redhat': (
            'sudo yum install',
            ('python2-pyaudio',
             'python3-pyaudio')),
        'arch': (
            'sudo packman -S',
            ('python2-pyaudio',
             'python-pyaudio')),
        'gentoo': (
            'sudo emerge --ask --verbose',
            ('pyaudio',
             'pyaudio')),
        'suse': (
            'sudo zypper install',
            ('python-PyAudio',
             'python3-PyAudio')),
        'debian': (
            'sudo apt-get install',
            ('python-pyaudio',
             'python3-pyaudio'))}

    distroid = distro.os_release_attr('id_like')

    for distribution, command in pm.items():
        base_command, packages_names = command
        if distribution in distroid:
            if len(sys.argv) > 1 and sys.argv[1] == 'py2':
                python_version = 0
            elif len(sys.argv) > 1 and sys.argv[1] == 'py3':
                python_version = 1
            else:
                print("Usage: python installpyaudio.py (py2/py3)")
                sys.exit(1)
            install_command = "{} {}".format(
                base_command, packages_names[python_version])
elif platform.system().lower() == "darwin":
    install_command = 'brew install portaudio'


if install_command is not None:
    print("Portaudio is required for voice control. On your system, it can be installed using:")
    print("> {}".format(install_command))
    answer = input("Install now? (y/n)")
    if answer == 'y':
        sys.exit(os.system(install_command))
    else:
        sys.exit(1)
else:
    print("Portaudio is required for voice control. We can't recognise your system.")
    print("Please install python-binding 'pyaudio' manually.")
    print("For more details go to the below link:-")
    print("https://people.csail.mit.edu/hubert/pyaudio/")
    input("continue ")
