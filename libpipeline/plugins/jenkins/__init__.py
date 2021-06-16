import logging
import requests
import json

from ..api.hooks import threaded_callback_on
from ...webui.hooks import WebUI_started, static_WebUI_rendered


LOGGER = logging.getLogger(__name__)


def required_build_info(settings):
    """ Checks if all settings required for producing build urls are set """
    try:
        return all([ settings.get('jenkins', setting) != '' for setting in ['url', 'job_name', 'build_num'] ])
    except KeyError:
        return False


def required_jenkins_settings(settings):
    """ Checks if all settings required for interacting with jenkins build are set """
    try:
        return all([ settings.get('jenkins', setting) != '' for setting in ['url', 'username', 'password', 'job_name', 'build_num'] ])
    except KeyError:
        return False


def get_build_url(settings):
    return f'{settings.get("jenkins", "url")}/job/{settings.get("jenkins", "job_name")}/{settings.get("jenkins", "build_num")}'


def get_build_log_url(settings):
    return f'{get_build_url(settings)}/console'


def set_webui_link_description(settings, event, URL, is_artifact=False):
    build_url = get_build_url(settings)
    submit_url = f'{build_url}/configSubmit'
    artifact_baseurl = f'{build_url}/artifact'
    if is_artifact:
        URL = f'{artifact_baseurl}/{URL}'
    payload = {
        'displayName': f'#{settings.get("jenkins", "build_num")}: {event}',
        'description': f'<a href="{URL}">WebUI</a>',
    }

    LOGGER.debug(f'Setting jenkins build info: {submit_url}; {str(payload)}')
    response = requests.post(submit_url, data={'Submit': 'save', 'json': json.dumps(payload)},
                             auth=(settings.get('jenkins', 'username'), settings.get('jenkins', 'password')))
    if response.status_code != 200:
        LOGGER.error(f'Can\'t set jenkins build name and description: {response.status_code}: {response.text}')


@threaded_callback_on(WebUI_started)
def set_jenkins_build_info(webUI):
    """ 
    This is hook callback reacting on WebUI_started.
    Sets jenkins build display_name and description to event name and link to webUI
    """
    settings = webUI.pipeline.settings

    if not required_jenkins_settings(settings):
        return

    set_webui_link_description(settings, webUI.pipeline.event, webUI.baseurl)


@threaded_callback_on(static_WebUI_rendered)
def set_jenkins_build_info_static_webui(pipeline, path):
    """ 
    This is hook callback reacting on WebUI_started.
    Sets jenkins build display_name and description to event name and link to webUI
    """
    settings = pipeline.settings

    if not required_jenkins_settings(settings):
        return

    set_webui_link_description(settings, pipeline.event, path, is_artifact=True)
