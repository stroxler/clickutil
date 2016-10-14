from __future__ import print_function
import functools

from ..argspec import with_argspec, get_argspec, wraps


def test_with_argspec():
    def dummy_decorator(f):
        "Return a wrapper that doesn't preserve the argspec"
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

    # check that default functools.wraps clobbers arg info
    @dummy_decorator
    def f_bad(x, y): pass

    bad_argspec = get_argspec(f_bad)
    assert 'x' not in bad_argspec.args

    # check that the with_argspec wrapper saves arg info
    @with_argspec
    def f_good(x, y): pass

    good_argspec = get_argspec(f_good)
    assert 'x' in good_argspec.args


def test_get_argspec():

    msg = "Works when there's no __argspec__ attribute"

    def f(x): pass
    expected = ['x']
    actual = get_argspec(f).args
    assert actual == expected, msg

    msg = "Works when there is an __argspec__ attribute"

    def f(x): pass
    f.__argspec__ = 'argspec'
    expected = 'argspec'
    actual = get_argspec(f)
    assert actual == expected, msg


def test_wraps():
    """
    Test the wraps annotation. This indirectly tests the
    update_wrapper function, so we can omit unit tests of the latter.
    """

    def functools_decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return 'wrapped'
        return wrapper

    def wrapping_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return 'wrapped'
        return wrapper

    @functools_decorator
    def f_lost_args(x, y): pass

    @wrapping_decorator
    def f_kept_args_one_level(x, y): pass

    @wrapping_decorator
    @wrapping_decorator
    def f_kept_args_two_levels(x, y): pass

    # make sure all of the functions actually got wrapped
    # (they would return None if they weren't wrapped)
    assert f_lost_args(0, 0) == 'wrapped'
    assert f_kept_args_one_level(0, 0) == 'wrapped'
    assert f_kept_args_two_levels(0, 0) == 'wrapped'

    good_args = ['x', 'y']
    bad_args = []

    # using a functools-built decorator should lose arg info
    actual = get_argspec(f_lost_args).args
    assert actual == bad_args

    # using a wrapping-built decorator should not lose arg info
    actual = get_argspec(f_kept_args_one_level).args
    assert actual == good_args

    # ...even if the annotations are stacked
    actual = get_argspec(f_kept_args_two_levels).args
    assert actual == good_args
