from plugin import plugin
from npm.bindings import npm_run


@plugin("electron")
def electron(jarvis, s):
    # Open a browser for creating a Jarvis GUI with HTML,CSS and Javascript
    print("Loading...")
    pkg = npm_run('start')
