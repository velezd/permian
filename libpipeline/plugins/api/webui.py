from ...webui import WebUI

def register_blueprint(blueprint, url_prefix=None):
    """
    Redirects to webui.WebUI.registerBlueprint

    TBD
    """
    return WebUI.registerBlueprint(blueprint, url_prefix)
