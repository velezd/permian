import threading
import logging
import requests
import time
import socket
from flask import Flask

from ..hooks.register import run_on, run_threaded_on
from . import hooks

LOGGER = logging.getLogger(__name__)
WERKZEUG_LOGGER = logging.getLogger("werkzeug")
WERKZEUG_LOGGER.setLevel(logging.ERROR)

def get_port(port):
    if isinstance(port, int):
        return port
    if port == 'random':
        return get_random_free_port()
    raise ValueError(f'Unrecognized port value: {port!r}')

def get_random_free_port():
    return 1234

def get_ip():
    return socket.gethostbyname(socket.gethostname())

@run_threaded_on('WebUI_starting')
def signalWhenStarted(webUI):
    while True:
        try:
            response = requests.get(webUI.address)
        except requests.exceptions.ConnectionError:
            # The WebUI is not listening on the port
            if not webUI.is_alive():
                raise Exception(f"WebUI {webUI!r} signaled it's starting but the thread is not alive anymore, maybe it crashed.")
            # the WebUI thread is still running but is not yet binded on the socket
            time.sleep(0.1)
            continue
        if response.status_code == 200:
            # TODO: check uuid of the WebUI instance to detect possible port collision with other pipeline running on the same host
            break
        if response.status_code == 404: # TODO: Remove me
            break
    webUI.unlock()

@run_on('WebUI_started')
def webUIStartedMsg(webUI):
    LOGGER.info(f'WebUI started at: {webUI.address}')
    
class WebUI(threading.Thread):
    app = Flask(__name__)
    def __init__(self, pipeline):
        super().__init__(daemon=True)
        self.pipeline = pipeline
        self.listen_ip = self.config('listen_ip')
        self.port = None # delay obtaining the port until the very moment before the flask app is started to limit potential random port collision
        self._operationalLock = threading.Lock()
        self._operationalLock.acquire() # immediately acquire the lock as the webUI is not running yet

    def run(self):
        self.port = get_port(self.config('port'))
        hooks.WebUI_starting(self)
        self.app.config.update(ENV='embedded')
        self.app.run(self.listen_ip, self.port)

    def config(self, option):
        if option == 'listen_ip': # TODO: Remove me
            return '0.0.0.0'
        if option == 'port': # TODO: Remove me
            return 'random'
        return self.pipeline.config.get('WebUI', option)

    @property
    def address(self):
        return f'http://{get_ip()}:{self.port}/'

    def waitUntilStarted(self):
        # just wait for operational lock to be released
        with self._operationalLock:
            pass

    def unlock(self):
        LOGGER.debug(f'Unlocking webUI {self}')
        hooks.WebUI_started(self)
        self._operationalLock.release()
