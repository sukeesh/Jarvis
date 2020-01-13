from colorama import Fore
from plugin import plugin


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

@plugin('talk faster')
def talk_faster(jarvis, s):
    if jarvis.is_voice_enabled():
        jarvis.change_speech_rate(40)
    else:
        jarvis.say("Type 'enable sound' to allow Jarvis to talk out loud.", Fore.BLUE)

@plugin('talk slower')
def talk_slower(jarvis, s):
    if jarvis.is_voice_enabled():
        jarvis.change_speech_rate(-40)
    else:
        jarvis.say("Type 'enable sound' to allow Jarvis to talk out loud.", Fore.BLUE)
        