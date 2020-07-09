import functools
import inspect
import itertools
import threading

HOOKS = {}
CALLBACKS = {}


def define(name=None):
    """
    Define hook and assing name to it.
    
    This should be used purely as function decorator where the defined function
    should have no body, as it will be replaced by a function which will call
    all callables assigned to hook of this name.

    Example of use::

      @hooks.define('process_started')
      def process_started_hook(pid, some_other_value=None):
          pass

    Or::
      @hooks.define()
      def process_started(pid, some_other_value=None):
          pass

    Where the second one would have name set to the name of the decorated
    function.

    :param name: Name under which the hook is registered, if not specified, name of the decorated function is used.
    :type name: str, optional
    :return: function decorator used for hook definition
    """
    # TODO: Fix kwargs, the default values are currently not being passed to callbacks
    def decorator(func):
        hook_name = name # this line is needed because if name was redefined, python would consider name as local variable in the decorator function and would later raise UnboundLocalError in following if statement
        if hook_name is None:
            hook_name = func.__name__
        @functools.wraps(func)
        def hook_function(*args, **kwargs):
            for callback in CALLBACKS[hook_name]:
                callback(*args, **kwargs)
        # remember the original function to be able to compare its signature when registering hook callback
        HOOKS[hook_name] = func
        # initialize list of callback function for the hook name
        CALLBACKS[hook_name] = []
        return hook_function
    return decorator

def run_on(name):
    """
    Assign callback function to hook of given name. This decorator compares the
    hook function signature with the callback function signature and if they
    are not compatible raises IncompatibleCallback exception.

    Important note: The callback has to have the same function signature as
    the hook including the default values, otherwise, the callback function will
    be considered as incompatible. This requirement is caused by limitation of
    passing default values in current implementation.

    The decorated callback has to be a function, partial function or object of
    callable class with compatible __call__ signature. Current implementation
    doesn't handle lambda functions or classmethods.

    :param name: Name of hook for which the callback should be called
    :type name: str
    :return: function decorator used for callback registration
    """
    def decorator(func):
        if not _compatible_signatures(func, HOOKS[name]):
            raise Exception('Incompatible hook and callback signatures')
        CALLBACKS[name].append(func)
        return func
    return decorator

def run_threaded_on(name):
    """
    Similar as run_on, but the callback is started as (non-daemon) thread.

    For more details see run_on.

    :param name: Name of hook for which the callback should be called
    :type name: str
    :return: function decorator used for callback registration
    """
    def decorator(func):
        if not _compatible_signatures(func, HOOKS[name]):
            raise Exception('Incompatible hook and callback signatures')
        @functools.wraps(func)
        def threaded_func(*args, **kwargs):
            threading.Thread(target=func, args=args, kwargs=kwargs).start()
        CALLBACKS[name].append(threaded_func)
        return func
    return decorator

def _compatible_signatures(func1, func2):
    return inspect.signature(func1) == inspect.signature(func2)
