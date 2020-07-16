from flask import current_app

def currentWebUI():
    """
    :return: Instance of :py:class:`WebUI` handling this request.
    :rtype: WebUI
    """
    return current_app.config['webUI']

def currentPipeline():
    """
    :return: Instance of :py:class:`Pipeline` related to this request.
    :rtype: libpipeline.pipeline.Pipeline
    """
    return current_app.config['pipeline']
