import platform
import sys

from helper import executable_exists


PackageManager = {
    "macos": "brew install",
    "linux": {
        "readhat": "sudo yum",
        "arch": "sudo pacman -S",
        "gentoo": "sudo emerge --ask --verbose",
        "suse": "sudo zypper install",
        "debian": "sudo apt-get install"
    }
}


LinuxDistroRecognition = {
    "yum": "redhat",
    "pacman": "arch",
    "emerge": "gentoo",
    "zypper": "suse",
    "apt-get": "debian"
}


PortAudio = {
    "name": "Voice Recorder",
    "pip": [
        'SpeechRecognition',
        "pyaudio --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib'"],
    "package_guess": {
        "macos": 'portaudio',
        "linux": {
            'redhat': 'python3-pyaudio python3-devel',
            'arch': 'python-pyaudio',
            'gentoo': 'pyaudio',
            'suse': 'python3-PyAudio python3-devel',
            'debian': 'python3-pyaudio python3-dev'
        }},
    "description": "Required for voice control",
    "instruction": """\
Please install python-binding 'pyaudio' manually."
For more details go to the below link:
https://people.csail.mit.edu/hubert/pyaudio/"""}


RequestsSecurity = {
    "name": "Requests security",
    "pip": ['requests[security]'],
    "description": "Better/saver https",
    "instruction": "https://stackoverflow.com/questions/31811949/pip-install-requestssecurity-vs-pip-install-requests-difference"
}


Fasttext = {
    "name": "Fasttext language recognition",
    "pip": ['fasttext'],
    "description": "Fasttext is a text classification library capable of detecting 176 languages.",
    "instructions": "https://github.com/facebookresearch/fastText/#requirements"
}


NativeNotification = {
    "name": "Notification",
    "executable": ['notify-send'],
    "description": "Native linux notifications",
    "instruction": "Please install 'notify-send' manually using your local package manager!",
    "package_guess": {
        "linux": {
            'redhat': 'libnotify',
            'arch': 'libnotify',
            'gentoo': 'eselect-notify-send',
            'suse': 'libnotify-tools',
            'debian': 'libnotify-bin'
        }
    }
}


FFMPEG = {
    "name": "ffmpeg",
    "executable": ['ffmpeg'],
    "description": "Download music as .mp3 instead .webm",
    "instruction": "Please install 'ffmpeg' manually using your local package manager!",
    "package_guess": {
        "macos": "ffmpeg",
        "linux": {
            'redhat': 'ffmpeg',
            'arch': 'ffmpeg',
            'gentoo': 'ffmpeg',
            'suse': 'ffmpeg',
            'debian': 'ffmpeg'
        }
    }
}


ESPEAK = {
    "name": "espeak",
    "executable": ['espeak'],
    "description": "Text To Speech for Jarvis to talk out loud (alternatives: sapi5 or nsss will work, too)",
    "instruction": "Please install 'espeak' manually using your local package manager!",
    "package_guess": {
        "linux": {
            'redhat': 'espeak',
            'arch': 'espeak',
            'gentoo': 'espeak',
            'suse': 'espeak',
            'debian': 'espeak'
        }
    }
}


WKHTMLTOPDF = {
    "name": "wkhtmltopdf",
    "executable": ['wkhtmltopdf'],
    "description": "Convert html file or web url into pdf ",
    "instruction": "Please install 'wkhtmltopdf' manually using your local package manager!",
    "package_guess": {
        "linux": {
            'redhat': 'wkhtmltopdf',
            'arch': 'wkhtmltopdf',
            'gentoo': 'wkhtmltopdf',
            'suse': 'wkhtmltopdf',
            'debian': 'wkhtmltopdf'
        }
    }
}

HTOP = {
    "name": "htop",
    "executable": ['htop'],
    "description": "Interactive system-monitor process-viewer and process-manager",
    "instruction": "Please install 'htop' manually using your local package manager!",
    "package_guess": {
        "linux": {
            'redhat': 'htop',
            'arch': 'htop',
            'gentoo': 'htop',
            'suse': 'htop',
            'debian': 'htop'
        }
    }
}


OPTIONAL_REQUIREMENTS = [PortAudio, RequestsSecurity, FFMPEG, ESPEAK, WKHTMLTOPDF, Fasttext, HTOP]


if not sys.platform == "darwin":
    OPTIONAL_REQUIREMENTS += [NativeNotification]


def get_guess(data):
    if sys.platform == "darwin":
        if 'macos' in data:
            return data['macos']
        else:
            return False
    elif platform.system().lower() == "linux":
        if 'linux' in data:
            data = data['linux']
        else:
            return False

        for executable, distro in LinuxDistroRecognition.items():
            if executable_exists(executable):
                if distro in data:
                    return data[distro]

    return False
