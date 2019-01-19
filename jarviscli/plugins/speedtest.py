import speedtest as st
import sys
import threading
import itertools
import time
from colorama import Fore
from plugin import plugin


class SpinnerThread(threading.Thread):
    """SpinnerThread class to show a spinner on command line while the progream is running"""
    def __init__(self, label="Hmmm... ", delay=0.2):
        super(SpinnerThread, self).__init__()
        self.label = label
        self.delay = delay
        self.running = False

    def start(self):
        self.running = True
        super(SpinnerThread, self).start()

    def run(self):
        chars = itertools.cycle(r'-\|/')
        while self.running:
            sys.stdout.write('\r' + self.label + next(chars))
            sys.stdout.flush()
            time.sleep(self.delay)

    def stop(self):
        self.running = False
        self.join()
        sys.stdout.write('\r')
        sys.stdout.flush()


@plugin(network=True)
def speedtest(jarvis, s):
    """Runs a speedtest on your internet connection"""
    try:
        res = st.Speedtest()
    except:
        return jarvis.connection_error()

    # Create a spinner on command line to show that its running
    spinner = SpinnerThread('Running the test ', 0.15)
    spinner.start()

    res.get_best_server()
    download_speed = res.download()
    upload_speed = res.upload()
    # results_dict = res.results.dict()

    spinner.stop()

    # Print the results
    jarvis.say('Speed test results:', Fore.GREEN)
    jarvis.say('Download: ' + pretty_speed(download_speed), Fore.GREEN)
    jarvis.say('Upload: ' + pretty_speed(upload_speed), Fore.GREEN)


def pretty_speed(speed):
    """ return speed value prettily accordingly in either bps, Kbps, Mbps, Gbps"""
    unit = 'bps'
    kmg = ['', 'K', 'M', 'G']
    i = 0
    while speed >= 1000:
        speed /= 1000
        i += 1
    return "{:.2f}".format(speed) + ' ' + kmg[i] + unit
