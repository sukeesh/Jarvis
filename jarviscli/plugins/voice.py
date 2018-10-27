from plugin import plugin

import os


@plugin()
def enable_sound(jarvis, s):
    """Let Jarvis use his voice."""
    jarvis.enable_voice()


@plugin()
def disable_sound(jarvis, s):
    """Deny Jarvis his voice."""
    jarvis.disable_voice()


@plugin()
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
