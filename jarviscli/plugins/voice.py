from colorama import Fore
from plugin import LINUX, UNIX, MACOS, WINDOWS, plugin, require


@plugin('enable sound')
def enable_sound(jarvis, s):
    """Let Jarvis use his voice."""
    jarvis.enable_voice()


@plugin('disable sound')
def disable_sound(jarvis, s):
    """Deny Jarvis his voice."""
    jarvis.disable_voice()


@plugin('say')
def say(jarvis, s):
    """Reads what is typed."""
    if not s:
        jarvis.say("What should I say?")
    else:
        voice_state = jarvis.is_voice_enabled()
        jarvis.enable_voice()
        jarvis.say(s)
        if not voice_state:
            jarvis.disable_voice()


@require(platform=[LINUX, WINDOWS])
@plugin('talk faster')
def talk_faster(jarvis, s):
    """Make Jarvis' speech engine talk faster.
    """
    if jarvis.is_voice_enabled():
        jarvis.change_speech_rate(40)
    else:
        jarvis.say("Type 'enable sound' to allow Jarvis to talk out loud.",
            Fore.BLUE)


@require(platform=[LINUX, WINDOWS])
@plugin('talk slower')
def talk_slower(jarvis, s):
    """Make Jarvis' speech engine talk slower.
    """
    if jarvis.is_voice_enabled():
        jarvis.change_speech_rate(-40)
    else:
        jarvis.say("Type 'enable sound' to allow Jarvis to talk out loud.",
            Fore.BLUE)
