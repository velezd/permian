from ... import hooks

def make(func):
    """
    Redirects to hooks.register.define

    TBD
    """
    return hooks.register.define(func)

def callback_on(hook_func):
    """
    Redirects to hooks.run_on

    TBD
    """
    return hooks.register.run_on(hook_func)

def threaded_callback_on(hook_func):
    """
    Redirects to hooks.run_threaded_on

    TBD
    """
    return hooks.register.run_threaded_on(hook_func)
