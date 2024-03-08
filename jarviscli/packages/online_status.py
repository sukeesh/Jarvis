import socket
import time


class OnlineStatus:
    RECHECK_TIMEOUT = 120

    def __init__(self):
        self.online_status = None
        self.last_checked = -1

    def get_online_status(self):
        if self.online_status is None:
            self.refresh()
        elif self.online_status is False:
            if self.last_checked + OnlineStatus.RECHECK_TIMEOUT < time.time():
                self.refresh()
        return self.online_status

    def refresh(self):
        self.online_status = self._has_internet()
        self.last_checked = time.time()

    def _has_internet(self):
        print('Check online status')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            socket.setdefaulttimeout(3)
            sock.connect(('9.9.9.9', 53))
            return True
        except socket.timeout as e:
            return False
        except OSError as e:
            return False
