import logging
from time import sleep
from ...hooks.register import run_threaded_on
from ...hooks.builtin import pipeline_ended

LOGGER = logging.getLogger(__name__)

@run_threaded_on(pipeline_ended)
def shutdownDelay(pipeline):
    """ This is hook callback reacting on hooks.pipeline_ended. Waits some time after pipeline finishes. """
    if pipeline.settings.getboolean('shutdownDelay', 'enabled'):
        delay = pipeline.settings.get('shutdownDelay', 'delay')
        LOGGER.info("Pipeline ended, waiting for %s seconds" % delay)
        sleep(int(delay))
