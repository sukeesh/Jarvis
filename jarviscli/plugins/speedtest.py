from colorama import Fore

import speedtest as st
from plugin import plugin, require


@require(network=True)
@plugin('speedtest')
def speedtest(jarvis, s):
    """Runs a speedtest on your internet connection"""
    try:
        res = st.Speedtest()
    except st.ConfigRetrievalError:
        return jarvis.connection_error()

    # Create a spinner on command line to show that its running
    jarvis.spinner_start('Running the test ')

    res.get_best_server()
    download_speed = res.download()
    upload_speed = res.upload()

    jarvis.spinner_stop('')

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
