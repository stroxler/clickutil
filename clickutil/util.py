from argspec import update_wrapper


def mk_decorator(click_decorator):
    """
    Add a call to argspec.update_wrapper to the output of a click
    decorator, in order to persist extra metadata.

    PARAMETERS
    ----------
    click_decorator : function
        A click decorator function, for example the return value to
        a call to `click.optioni`

    """
    def decorator(f):
        wrapper = click_decorator(f)
        update_wrapper(wrapper, f)
        return wrapper
    return decorator
