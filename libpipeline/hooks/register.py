import functools
import inspect
import itertools
import threading

HOOKS = {}
CALLBACKS = {}

def define(func):
    """
    Define hook function.
    
    This should be used purely as function decorator where the defined function
    should have no body, as it will be replaced by a function which will call
    all callables assigned to this hook.

    Example of use::

      @hooks.define
      def process_started(pid, some_other_value=None):
          pass

    :param func: Function which will be transformed to hook
    :type func: function
    :return: Hook function which when called calls all associated callbacks
    """
    @functools.wraps(func)
    def hook_function(*args, **kwargs):
        for callback in CALLBACKS[hook_function]:
            callback(*args, **kwargs)
    # remember the original function to be able to compare its signature when registering hook callback
    HOOKS[hook_function] = func
    # initialize list of callback function for the hook name
    CALLBACKS[hook_function] = []
    return hook_function

def run_on(hook_func):
    """
    Assign callback function to given hook_func. This decorator compares the
    hook function signature with the callback function signature and if they
    are not compatible raises IncompatibleCallback exception.

    Important note: The callback has to have the same function signature as
    the hook including the default values, otherwise, the callback function will
    be considered as incompatible. This requirement is caused by limitation of
    passing default values in current implementation.

    The decorated callback has to be a function, partial function or object of
    callable class with compatible __call__ signature. Current implementation
    doesn't handle lambda functions or classmethods.

    :param hook_func: Hook function for which the callback should be called
    :type hook_func: function
    :return: function decorator used for callback registration
    """
    def decorator(func):
        if not _compatible_signatures(func, HOOKS[hook_func]):
            raise Exception('Incompatible hook and callback signatures')
        CALLBACKS[hook_func].append(func)
        return func
    return decorator

def run_threaded_on(hook_func):
    """
    Similar as run_on, but the callback is started as (non-daemon) thread.

    For more details see run_on.

    :param hook_func: Hook function for which the callback should be called
    :type hook_func: function
    :return: function decorator used for callback registration
    """
    def decorator(func):
        if not _compatible_signatures(func, HOOKS[hook_func]):
            raise Exception('Incompatible hook and callback signatures')
        @functools.wraps(func)
        def threaded_func(*args, **kwargs):
            threading.Thread(target=func, args=args, kwargs=kwargs).start()
        CALLBACKS[hook_func].append(threaded_func)
        return func
    return decorator

def _compatible_signatures(func1, func2):
    return inspect.signature(func1) == inspect.signature(func2)
