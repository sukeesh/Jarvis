import distro
import os
import platform

if platform.system().lower() == "linux":
    pm = {}
    distroid = distro.os_release_attr('id_like')
    pm['redhat'] = 'sudo yum install '
    pm['arch'] = 'sudo pacman -S '
    pm['gentoo'] = 'sudo emerge --ask --verbose '
    pm['suse'] = 'sudo zypper install '
    pm['debian'] = 'sudo apt-get install '
    print('Installing python-pyaudio python3-pyaudio')
    os.system(pm[distroid] + 'python-pyaudio python3-pyaudio')
elif platform.system().lower() == "Darwin":
    print('Installing python-pyaudio python3-pyaudio')
    os.system('brew install portaudio')
