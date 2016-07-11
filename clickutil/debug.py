from .args import boolean_flag
from inspectcall import wraps
import calldecorators


def debug(default_debug=False, delay=3, use_debugger=None):
    """
    Add a click handler to drop into a debugger on uncaught
    exceptions. You can toggle this on and off using the
    --debug/--no-debug flag; the default value is controled by
    the `default_debug` parameter.

    PARAMETERS
    ----------
    default_debug : boolean
        Default value of the debug flag.
    delay : int
        How many seconds to wait after printing the stack trace
        and before dropping into the debugger. Setting this nonzero
        gives users a chance to keyboard interrupt if they don't need
        to debug after seeing a stack trace and error message.
    use_debugger : {module, None}
        The debugging module to use. If None, then we use the
        calldecorators defaults: first we try `pudb`, and if it is not
        installed we use `pdb`.

    """
    def decorator(f):

        @wraps(f)
        @boolean_flag(
            '--debug', default=default_debug,
            help='drop into pudb / pdb post-mortem on uncaught errors?'
        )
        def wrapped(debug, *args, **kwargs):
            if debug:
                return calldecorators.debug(
                    delay=delay,
                    use_debugger=use_debugger
                )(f)(*args, **kwargs)
            else:
                return f(*args, **kwargs)

        return wrapped

    return decorator
