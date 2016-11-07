"""
Base decorators for use with clickutil.
"""
import wrapt


def call(target):
    """
    Tool to wrap a call to `target` as a decorator on a placeholder function.

    This is useful because if you decorate `target` directly, then it becomes
    unavailable in the namespace where you do the decoration, whereas
    decorating a placeholder works well.

    For example:

    @call(target)
    def _target(): pass

    Can be used to wrap a call to `target` inside a click command without
    loosing `target` in the current namespace.

    """
    def decorator(placeholder):
        @wrapt.decorator
        def make_wrapper(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs)

        wrapper = make_wrapper(target)
        wrapper.__name__ = placeholder.__name__
        wrapper.__module__ = placeholder.__module__
        return wrapper
    return decorator


def use_output(target):
    """
    Tool to wrap a call to `target` as a decorator on a function that
    does something with its output.

    This is similar to the `call` decorator, except that it lets the
    click endpoint do something custom with the output. This is useful
    if you have a python api that returns information about something,
    for example as a list or dict, but the command-line interface
    needs to print that data.

    For example:

    @call(target)
    def _target(output):
        for thing in output:
            print(thing)

    """
    def decorator(placeholder):
        @wrapt.decorator
        def make_wrapper(wrapped, instance, args, kwargs):
            output = wrapped(*args, **kwargs)
            placeholder(output)
            return output

        wrapper = make_wrapper(target)
        wrapper.__name__ = placeholder.__name__
        wrapper.__module__ = placeholder.__module__
        return wrapper

    return decorator
