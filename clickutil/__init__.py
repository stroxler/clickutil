import click


EXISTING_FILE = click.Path(exists=True, dir_okay=False, file_okay=True)
EXISTING_DIR = click.Path(exists=True, dir_okay=True, file_okay=False)
NEW_FILE_OR_DIR = click.Path(exists=False)

def default_option(flag, short_flag, type, default, help):
    """
    Consistent interface for creating click options with defaults.
    """
    if short_flag is None:
        return click.option(flag,
                            type=type, default=default,
                            help=help, show_default=True)
    else:
        return click.option(flag, short_flag,
                            type=type, default=default,
                            help=help, show_default=True)


def required_option(flag, short_flag, type, help):
    """
    Consistent interface for creating click options without defaults.
    """
    if short_flag is None:
        return click.option(flag,
                            type=type, required=True,
                            help=help, show_default=True)
    else:
        return click.option(flag, short_flag,
                            type=type, required=True,
                            help=help, show_default=True)


def boolean_flag(flag, default, help):
    """
    Consistent interface for creating boolean flags using click.
    """
    if not flag.startswith('--'):
        raise ValueError('flag {} does not start with "--"'.format(flag))
    stripped_flag = flag[2:]
    click_flag = '--{0}/--no-{0}'.format(stripped_flag)
    return click.option(click_flag, default=default, help=help,
                        show_default=True)


def call(f):
    """
    Tool to wrap a call to `f` as a decorator on a placeholder function.

    This is useful because if you decorate `f` directly, then it becomes
    unavailable in the namespace where you do the decoration, whereas
    decorating a placeholder works well.

    For example:

    @wrap_as_click_decorator(f)
    def _f(): pass

    Can be used to wrap a call to f inside a click command without loosing
    `f` in the current namespace.

    """
    def decorator(placeholder):
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        wrapped.__doc__ = f.__doc__
        wrapped
        return wrapped
    return decorator


def debug(default_debug=False, delay=3):
    """
    Add a click option to drop into a debugger on uncaught exceptions
    in a click handler, when the --debug flag is set (the default value
    is configurable, which makes it easier to set up a development
    environment where it's always true).

    There's a `delay`-second delay so that you can see the traceback and
    possibly keyboard interrupt if you don't need a debug session.
    """
    def decorator(f):

        @boolean_flag(
            '--debug', default=default_debug,
            help='drop into pudb / pdb post-mortem on uncaught errors?'
        )
        def wrapped(debug, *args, **kwargs):
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
                    debugger = get_debugger()
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
