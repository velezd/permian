import logging
import requests
import json

from ..api.hooks import threaded_callback_on
from ...webui.hooks import WebUI_started


LOGGER = logging.getLogger(__name__)


@threaded_callback_on(WebUI_started)
def set_jenkins_build_info(webUI):
    """ 
    This is hook callback reacting on WebUI_started.
    Sets jenkins build display_name and description to event name and link to webUI
    """
    settings = webUI.pipeline.settings

    if not required_jenkins_settings(settings):
        return

    build_num = settings.get('jenkins', 'build_num')
    url = f'{settings.get("jenkins", "url")}/job/{settings.get("jenkins", "job_name")}/{build_num}/configSubmit'
    payload = {'displayName': f'#{build_num}: {str(webUI.pipeline.event)}',
               'description': f'WebUI: <a href="{webUI.baseurl}">{webUI.baseurl}</a>'}

    LOGGER.debug(f'Setting jenkins build info: {url}; {str(payload)}')
    response = requests.post(url, data={'Submit': 'save', 'json': json.dumps(payload)},
                             auth=(settings.get('jenkins', 'username'), settings.get('jenkins', 'password')))
    if response.status_code != 200:
        LOGGER.error(f'Can\'t set jenkins build name and description: {response.status_code}: {response.text}')


def required_jenkins_settings(settings):
    """ Checks if all settings required for interacting with jenkins build are set """
    try:
        return all([ settings.get('jenkins', setting) != '' for setting in ['url', 'username', 'password', 'job_name', 'build_num'] ])
    except KeyError:
        return False
