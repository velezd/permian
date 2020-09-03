import logging
import requests
import time

from ..hooks.register import run_on, run_threaded_on
from . import hooks

LOGGER = logging.getLogger(__name__)
# following lines should be controllable by settings
WERKZEUG_LOGGER = logging.getLogger("werkzeug")
WERKZEUG_LOGGER.setLevel(logging.ERROR)

@run_threaded_on(hooks.WebUI_starting)
def signalWhenStarted(webUI):
    """
    This is hook callback reacting on :py:func:`hooks.WebUI_starting`.

    When the webUI begins starting process, start checking for its availability.
    Once the webUI starts (checking the desired instance is running on the
    expected port), unlock the webUI effectively signalling to others that the
    webUI is fully initialized and ready to accept requests.
    """
    while True:
        try:
            response = requests.get(f'{webUI.baseurl}webUIuuid') # TODO: Fix the URL creation
        except requests.exceptions.ConnectionError:
            # The WebUI is not listening on the port
            if not webUI.is_alive():
                raise Exception(f"WebUI {webUI!r} signaled it's starting but the thread is not alive anymore, maybe it crashed.")
            # the WebUI thread is still running but is not yet binded on the socket
            time.sleep(0.1)
            continue
        if response.status_code == 200:
            # TODO: check uuid of the WebUI instance to detect possible port collision with other pipeline running on the same host
            if response.text != webUI.uuid:
                raise Exception("UUID of the webUI doesn't match. There's some other application/webUI running on the expected port!")
            break
        continue
    webUI.unlock()

@run_on(hooks.WebUI_started)
def webUIStartedMsg(webUI):
    """
    This is hook callback reacting on hooks.WebUI_started.

    Log URL of available webUI.
    """
    LOGGER.info(f'WebUI started at: {webUI.baseurl}')

# TODO: Remove this and possibly move to plugin
@run_on(hooks.WebUI_started)
def waitAWhile(webUI):
    """
    This is hook callback reacting on hooks.WebUI_started.

    Wait some time after webUI is started effectively blocking the pipeline to
    be finished for this time as the pipeline is waiting for all hooks to be
    finished.

    This callback should be removed and moved to plugin and also the waiting
    should not be enabled by default.
    """
    time.sleep(30)
