from os import system

from plugin import LINUX, MACOS, plugin


@plugin(plattform=LINUX, native="pactl")
def increase_volume__LINUX(jarvis, s):
    """Increases your speaker's sound."""
    system("pactl -- set-sink-volume 0 +3%")


@plugin(plattform=MACOS, native="osascript")
def increase_volume__MAC(jarvis, s):
    """Increases your speaker's sound."""
    system(
        'osascript -e "set volume output volume '
        '(output volume of (get volume settings) + 10) --100%"'
    )


@plugin(plattform=LINUX, native="pactl")
def decrease_volume__LINUX(jarvis, s):
    """Decreases your speaker's sound."""
    system("pactl -- set-sink-volume 0 -10%")


@plugin(plattform=MACOS, native="osascript")
def decrease_volume__MAC(jarvis, s):
    """Decreases your speaker's sound."""
    system(
        'osascript -e "set volume output volume '
        '(output volume of (get volume settings) - 10) --100%"'
    )


@plugin(plattform=LINUX, native="pactl")
def mute(jarvis, s):
    """Mute: Silence your speaker's sound."""
    system("pactl -- set-sink-mute 0 toggle")
