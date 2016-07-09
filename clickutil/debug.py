from .args import boolean_flag
from .wrapping import wraps


def debug(default_debug=False, delay=3, use_debugger=None):
    """
    Add a click option to drop into a debugger on uncaught exceptions
    in a click handler, when the --debug flag is set (the default value
    is configurable, which makes it easier to set up a development
    environment where it's always true).

    There's a `delay`-second delay so that you can see the traceback and
    possibly keyboard interrupt if you don't need a debug session.

    The use_debugger arg allows you to specify a debugger module. By
    default, we attempt to use pudb and fall back to pdb (see get_debugger).
    """
    def decorator(f):

        @wraps(f)
        @boolean_flag(
            '--debug', default=default_debug,
            help='drop into pudb / pdb post-mortem on uncaught errors?'
        )
        def wrapped(debug, *args, **kwargs):
            @debug
            def inner_wrapped
                return f

            if debug:
                try:
                    f(*args, **kwargs)
                except:
                    import sys
                    import traceback
                    import time
                    traceback.print_exc()
                    print ("\nSleeping for %d seconds before debug, press C-c "
                           " to exit") % delay
                    time.sleep(delay)
                    _, _, tb = sys.exc_info()
                    if use_debugger is None:
                        debugger = get_debugger()
                    else:
                        debugger = use_debugger
                    debugger.post_mortem(tb)
            else:
                f(*args, **kwargs)
        wrapped.__doc__ = f.__doc__
        return wrapped

    return decorator


def get_debugger():
    """
    Get a debugger for use in the debug wrapper. Factoring this out
    of the debug wrapper makes it a bit more pluggable, especially
    for tests.
    """
    try:
        import pudb
        return pudb
    except ImportError:
        print ("Using pudb not found, using pdb for post-mortem. "
               "Try pip install pudb.")
        import pdb
        return pdb
