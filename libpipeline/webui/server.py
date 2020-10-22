import uuid
from flask import Flask
import threading
import socket
import logging
import socket

from . import hooks

LOGGER = logging.getLogger(__name__)

class WebUI(threading.Thread):
    """
    Web UI for the pipeline. This class is designed as container for the flask
    app running in thread providing interface for the flask app instance and
    the HTTP server used for the interface where one can obtain baseurl of the
    server or wait for the server to start.

    The class also work as bridge between the flask app and pipeline instance
    associated to it using flask config to pass the pipeline instance, see
    :py:func:`currentPipeline` and :py:func:`currentWebUI`.

    :param pipeline: Pipeline instance for which the web UI should provide interface.
    :type pipeline: libpipeline.pipeline.Pipeline
    """
    blueprints=[]

    @classmethod
    def registerBlueprint(cls, blueprint):
        """
        Extend the webUI by providing flask Blueprint. There's no way to provide
        url_prefix at this point and it should be set in the Blueprint itself.

        The blueprints are registered to the app in the order they are
        registered via this method starting with pipeline builtin blueprints
        and then the plugin blueprints (in the order of plugins being loaded).

        :param blueprint: Flask Blueprint instance extending the webUI flask app
        :type blueprint: flask.Blueprint
        """
        cls.blueprints.append(blueprint)
        return blueprint

    def __init__(self, pipeline):
        super().__init__(daemon=True)
        self.app = Flask(__name__)
        for blueprint in self.blueprints:
            self.app.register_blueprint(blueprint)
        self.pipeline = pipeline
        self.listen_ip = self.config('listen_ip')
        self.port = None # delay obtaining the port until the very moment before the flask app is started to limit potential random port collision
        self._operationalLock = threading.Lock()
        self._operationalLock.acquire() # immediately acquire the lock as the webUI is not running yet
        self.uuid = uuid.uuid4().hex
        self.app.config.update(
            ENV='embedded',
            pipeline=self.pipeline,
            webUI=self,
        )

    def run(self):
        """
        The function that's executed in the thread. Call the
        :py:meth:`~WebUI.start` method instead of this one.
        For more info see python :py:class:`threading.Thread`.
        """
        self.port = get_port(self.config('listen_port'))
        hooks.WebUI_starting(self)
        self.app.run(self.listen_ip, self.port)

    def config(self, option):
        """

        """
        return self.pipeline.settings.get('WebUI', option)

    @property
    def baseurl(self):
        """

        """
        return f'http://{get_ip()}:{self.port}/'

    def waitUntilStarted(self):
        """

        """
        # just wait for operational lock to be released
        with self._operationalLock:
            pass

    def unlock(self):
        """

        """
        LOGGER.debug(f'Unlocking webUI {self}')
        hooks.WebUI_started(self)
        self._operationalLock.release()

def get_port(port_spec):
    """
    Provide port number based on the `port_spec` parameter. If the provided port
    is string 'random' then random available port is returned.

    In future this function could possibly also accept tuple (or range) as
    `port_spec` choosing available port from the provided range.

    :param port_spec:
    :type port_spec: int or str
    :return: port number
    :rtype: int
    """
    try: # try first to convert the string to number
        port_spec = int(port_spec)
    except ValueError:
        pass
    if isinstance(port_spec, int):
        return port_spec
    if port_spec == 'random':
        return get_random_free_port()
    raise ValueError(f'Unrecognized port value: {port_spec!r}')

def get_random_free_port():
    """
    Finds free port, There is possibility for a race condition,
    since another process may grab that port before it is used by Flask.

    :return: Port number of random available (currently unused) port
    :rtype: int
    """
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    port = tcp.getsockname()[1]
    tcp.close()
    return port

def get_ip():
    """
    :return: IP address of the host which should be reachable from outside.
    :rtype: str
    """
    return socket.gethostbyname(socket.gethostname())
