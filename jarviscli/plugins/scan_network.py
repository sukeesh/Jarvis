import nmap
from plugin import plugin, require, LINUX
from colorama import Fore


def error_output(jarvis, nm_scan) -> None:
    jarvis.say('Please, check your input is correct\n', Fore.RED)
    jarvis.say('This might hint what the problem is:\n', Fore.YELLOW)
    jarvis.say(str(nm_scan.scaninfo()['error']), Fore.YELLOW)


def show_output(jarvis, results: dict) -> None:
    uphosts: str = results['nmap']['scanstats']['uphosts']
    jarvis.say('Number of hosts up: ' + uphosts + '\n', Fore.GREEN)
    devices: dict = results['scan']
    for d in devices:
        jarvis.say(d, Fore.GREEN)
        jarvis.say('\tName: ' + devices[d]['hostnames'][0]['name'], Fore.GREEN)
        # Check if there are open tcp ports (handle error when no TCP ports)
        if 'tcp' in devices[d]:
            tcp_ports: dict = devices[d]['tcp']
            for port in tcp_ports:
                jarvis.say('\tOpen TCP Port: ' + str(port), Fore.GREEN)
                jarvis.say('\t\tProtocol Name: ' + tcp_ports[port]['name'], Fore.GREEN)
                jarvis.say('\t\tProduct: ' + tcp_ports[port]['product'], Fore.GREEN)
                jarvis.say('\t\tVersion: ' + tcp_ports[port]['version'], Fore.GREEN)
        print('----------------------------\n')


@require(network=True)
@require(native="nmap", platform=LINUX)
@plugin('scan_network')
def scan(jarvis, s: str) -> None:
    """
    Scans provided network for all connected devices
    Usage example: jarvis scan_network 172.16.1.10/24
    """
    # can't import top level since this import only works
    # if nmap is installed
    from nmap import PortScanner
    nm_scan: PortScanner = nmap.PortScanner()
    jarvis.say('Please wait, this might take a while!')
    if not s:
        jarvis.say('You need to provide address as input!\n'
                   ' For example: jarvis scan_network x.x.x.x/24', Fore.YELLOW)
    else:
        # for speedup replace the below line with:
        # nm_scan.scan(s, arguments='')
        # NOTE: this will provide less details
        nm_scan.scan(s)
        if 'error' in nm_scan.scaninfo():
            error_output(jarvis, nm_scan)

        # remove services field as it might contain
        # a lot of unneeded information
        nm_scan.scaninfo()['tcp'].pop('services')
        results: dict = nm_scan._scan_result
        show_output(jarvis, results)
