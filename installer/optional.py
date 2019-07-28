import platform
import sys

from helper import executable_exists


PackageManager = {
    "macos": "brew install",
    "linux": {
        "readhat": "sudo yum",
        "arch": "sudo packman -S",
        "gentoo": "sudo emerge --ask --verbose",
        "suse": "sudo zypper install",
        "debian": "sudo apt-get install"
    }
}


LinuxDistroRecognition = {
    "yum": "redhat",
    "packman": "arch",
    "emerge": "gentoo",
    "zypper": "suse",
    "apt-get": "debian"
}


PortAudio = {
    "name": "Voice Recorder",
    "pip": ['SpeechRecognition', "pyaudio --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib'"],
    "package_guess": {
        "macos": ['portaudio' 'portaudio'],
        "linux": {
            'redhat': ['python2-pyaudio python2-devel', 'python3-pyaudio python3-devel'],
            'arch': ['python2-pyaudio', 'python-pyaudio'],
            'gentoo': ['pyaudio', 'pyaudio'],
            'suse': ['python-PyAudio python-devel', 'python3-PyAudio python3-devel'],
            'debian': ['python-pyaudio python-dev', 'python3-pyaudio python3-dev']
        }
    },
    "description": "Required for voice control",
    "instruction": """\
Please install python-binding 'pyaudio' manually."
For more details go to the below link:
https://people.csail.mit.edu/hubert/pyaudio/"""
}


RequestsSecurity = {
    "name": "Requests security",
    "pip": ['requests[security]'],
    "description": "Better/saver https",
    "instruction": "More details: https://stackoverflow.com/questions/31811949/pip-install-requestssecurity-vs-pip-install-requests-difference"
}


NativeNotification = {
    "name": "Notification",
    "executable": ['notify-send'],
    "description": "Native linux notifications",
    "instruction": ""
}


FFMPEG = {
    "name": "ffmpeg",
    "executable": ['ffmpeg'],
    "description": "Download music as .mp3 instead .webm",
    "instruction": ""
}


ESPEAK = {
    "name": "espeak",
    "executable": ['espeak'],
    "description": "Text To Speech for Jarvis to talk out loud (alternatives: sapi5 or nsss will work, too)",
    "instruction": ""
}


OPTIONAL_REQUIREMENTS = [PortAudio, RequestsSecurity, FFMPEG, ESPEAK]


if not sys.platform == "darwin":
    OPTIONAL_REQUIREMENTS += [NativeNotification]


def get_guess(data):
    if sys.platform == "darwin":
        return data['macos']
    elif platform.system().lower() == "linux":
        data = data['linux']

        for executable, distro in LinuxDistroRecognition.items():
            if executable_exists(executable):
                return data[distro]

    return False
