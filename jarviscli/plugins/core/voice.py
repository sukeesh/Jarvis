from colorama import Fore

from plugin import Platform, plugin, require
from frontend.voice_control import GTTS_KEY

VOICE_ENABLED_KEY = 'voice_status'
VOICE_MODULE = 'voice'



def is_voice_enabled(jarvis):
    return VOICE_MODULE in jarvis.active_frontends


def get_voice(jarvis):
    return jarvis.active_frontends[VOICE_MODULE]


@plugin('enable sound')
def enable_sound(jarvis, s):
    """Let Jarvis use his voice."""
    jarvis.activate_frontend('voice')
    jarvis.update_data(VOICE_ENABLED_KEY, True)

    jarvis.say(Fore.BLUE + "Jarvis uses Googles speech engine.\nDo you consent with data "
               + "collection when Jarvis talks out loud? If yes, type:" + Fore.RED + " enable gtts")
    jarvis.say(Fore.BLUE + "If not, Jarvis will talk using the built-in speech engine. "
               + " If you wish to disable GTTS, type: " + Fore.RED + "disable gtts")


@plugin('disable sound')
def disable_sound(jarvis, s):
    """Deny Jarvis his voice."""
    jarvis.update_data(VOICE_ENABLED_KEY, False)
    jarvis.disable_frontend("voice")


@plugin('say')
def say(jarvis, s):
    """Reads what is typed."""
    # TODO!!!!
    if not s:
        jarvis.say("What should I say?")
    else:
        voice_state = jarvis.is_voice_enabled()
        jarvis.enable_voice()
        jarvis.say(s)
        if not voice_state:
            jarvis.disable_voice()


@plugin('disable gtts')
def disable_gtts(jarvis, s):
    """Reads what is typed without using gtts."""
    jarvis.update_data(GTTS_KEY, False)


@plugin('enable gtts')
def gtts(jarvis, s):
    """Reads what is typed using gtts."""
    jarvis.update_data(GTTS_KEY, True)


def change_speed(jarvis, s):
    if is_voice_enabled(jarvis):
        voice = get_voice(jarvis)
        get_voice(jarvis).change_speech_rate(s)
        jarvis.update_data('speech_rate', voice.speech_rate)
    else:
        jarvis.say("Type 'enable sound' to allow Jarvis to talk out loud.",
                   Fore.BLUE)


@require(platform=[Platform.LINUX, Platform.WINDOWS])
@plugin('talk faster')
def talk_faster(jarvis, s):
    """Make Jarvis' speech engine talk faster."""
    change_speed(jarvis, 40)


@require(platform=[Platform.LINUX, Platform.WINDOWS])
@plugin('talk slower')
def talk_slower(jarvis, s):
    """Make Jarvis' speech engine talk slower."""
    change_speed(jarvis, -40)
