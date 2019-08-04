import sys, os 
import threading
import subprocess
from plugin import plugin
from npm.bindings import npm_run
from subprocess import call


@plugin("electron")
def electron(jarvis, s):
    try:
        ElectronThread = threading.Thread(target = launchElectron)
        NodeThread = threading.Thread(target = callToNode)
        ElectronThread.start()
        NodeThread.start()
        NodeThread.join()
        #ElectronThread.join()
        #NodeThread.stop()
        #ElectronThread.stop()
    except:
        print('GUI has been closed')
        try:
            ElectronThread.stop()
        except:
            print('Destroying threads')

def launchElectron():
    # Open a browser for creating a Jarvis GUI with HTML,CSS and Javascript
    print("Loading...")
    pkg = npm_run('start')

def callToNode():
    # Call to the Node chatbot
    cwd = os.getcwd() 
    call(["node", cwd + "/examples/console-bot/"])   

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
