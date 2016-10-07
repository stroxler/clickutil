"""
Base decorators for use with clickutil.
"""
import wrapt
from inspectcall import wraps


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


def call(f):
    """
    Tool to wrap a call to `f` as a decorator on a placeholder function.

    This is useful because if you decorate `f` directly, then it becomes
    unavailable in the namespace where you do the decoration, whereas
    decorating a placeholder works well.

    For example:

    @call(f)
    def _f(): pass

    Can be used to wrap a call to f inside a click command without loosing
    `f` in the current namespace.

    """
    def decorator(placeholder):
        @wrapt.decorator
        def make_wrapper(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        wrapper = make_wrapper(f)
        wrapper.__name__ = placeholder.__name__
        wrapper.__module__ = placeholder.__module__
        return wrapper
    return decorator
