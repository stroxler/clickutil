"""
Variations on functools.update_wrapper and functools.wrap which attempt to
preserve argument information.

In general, the `wrapt` package has much better tooling for handling metadata
in decorators, but `wrapt` assumes that decorators are plain wrapper
functions. As a result, applying `wrapt` to `click` decorators does not work,
since the output of a `click` decorator isn't a wrapper function but rather
an object.

So this module avoids the issue by finding a function's argspec using
`inspect.getargspe`, and attaching it as metadata under the `__argspec__`
key (which isn't a traditional key for python object). This suffices for
the purposes of clickutil.

"""
import functools
import inspect


WRAPPER_ASSIGNMENTS = functools.WRAPPER_ASSIGNMENTS
WRAPPER_UPDATES = functools.WRAPPER_UPDATES


def with_argspec(f):
    """
    Create a decorated version of `f` whose `__argspec__` field is
    set. This allows users to make use of the clickutil.option and
    clickutil.boolean decorators, which rely on that field, without
    using clickutil.call

    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapped


def update_wrapper(wrapper,
                   wrapped,
                   assigned=WRAPPER_ASSIGNMENTS,
                   updated=WRAPPER_UPDATES):
    """
    Provides the same functionality as functools.update_wrapper,
    except it also sets an __argspec__ field based on the output
    of `get_argspec`.

    PARAMETERS
    ----------
    wrapper : function
        A function wrapping a target function. Often, wrapper
        is the output of a decorator.
    wrapped : function
        A function being wrapped, often the target of a decorator.
    assigned : list
        Fields to assign in `wrapper`. Usually this can be left
        as the default (which comes from `functools`).
    updated : list
        Fields to update in `wrapper`. Usually this can be left
        as the default (which comes from `functools`).

    RETURNS
    -------
    wrapper : function
        A reference to the `wrapper` input, which has also been
        modified as a side-effect.

    """
    wrapper = functools.update_wrapper(wrapper, wrapped, assigned, updated)
    setattr(wrapper, '__argspec__', get_argspec(wrapped))
    return wrapper


def wraps(wrapped,
          assigned=WRAPPER_ASSIGNMENTS,
          updated=WRAPPER_UPDATES):
    """
    Creates a decorator from `update_wrapper`, in the same manner that
    `functools.wraps` creates a decorator from `functools.update_wrapper`.

    PARAMETERS
    ----------
    See `update_wrapper`

    RETURNS
    -------
    A decorator which can be applied to a wrapper function. It takes
    the target of the wrapping as an input.

    EXAMPLE
    -------

    Here's how you would use `@wraps` inside a simple decorator:

    >>> def my_decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                print "Wrapping %s" % f.__name__
                return f(*args, **kwargs)
            return wrapped

    NOTES
    -----
    See the `get_argspec` docs for caveats about stacking decorators.

    """
    return functools.partial(update_wrapper, wrapped=wrapped,
                             assigned=assigned, updated=updated)


def get_argspec(f):
    """
    If `f` has an `__argspec__` field, return it. Otherwise,
    return `inspec.getargspec(f)`.

    PARAMETERS
    ----------
    f : function
        Here `f` can be a regular python function or method. It
        cannot be an arbitrary callable, because not all callables
        have arguments that can be inspected.

    NOTES
    -----
    If `f` is the output of a decorator which did not use `update_wrapper`,
    then most likely the original argument information from the target has
    already been lost. Decorators that require call information should
    always be at the bottom if you are using multiple decorators, and
    they should all use `@wraps` rather than `@functools.wraps` in order
    to ensure that the original arguments remain available.

    """
    if hasattr(f, '__argspec__'):
        return getattr(f, '__argspec__')
    else:
        return inspect.getargspec(f)
