import platform
import sys


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


PortAudio = {
    "name": "Voice Recorder",
    "pip": ['SpeechRecognition', "pyaudio --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib'"],
    "package_guess": {
        "macos": ['portaudio' 'portaudio'],
        "linux": {
            'redhat': ['python2-pyaudio', 'python3-pyaudio'],
            'arch': ['python2-pyaudio', 'python-pyaudio'],
            'gentoo': ['pyaudio','pyaudio'],
            'suse': ['python-PyAudio', 'python3-PyAudio'],
            'debian': ['python-pyaudio', 'python3-pyaudio']
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
        distroid = distro.os_release_attr('id_like')
        data = data['linux']

        for distribution, data in data.items():
            if distribution in distroid:
                return data

    return False
