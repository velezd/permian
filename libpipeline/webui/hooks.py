from ..hooks.register import define as define_hook

@define_hook()
def WebUI_starting(webUI):
    """
    WebUI is about to be started but is not accesible yet.

    You're most probably the hook looking for is WebUI_started as this hook is
    mainly used internaly to start checking for WebUI to be started invoking
    then the WebUI_started hook.
    """
    pass

@define_hook()
def WebUI_started(webUI):
    """
    WebUI is running and ready to accept requests
    """
    pass
