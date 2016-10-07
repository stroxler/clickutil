import functools

import inspectcall

from ..call import with_argspec, call


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

    bad_argspec = inspectcall.get_argspec(f_bad)
    assert 'x' not in bad_argspec.args

    # check that the with_argspec wrapper saves arg info
    @with_argspec
    def f_good(x, y): pass

    good_argspec = inspectcall.get_argspec(f_good)
    assert 'x' in good_argspec.args


def test_call():
    def f(x, y):
        "f documentation"
        return 'x is {}'.format(x)

    @call(f)
    def _f(): pass

    # check that _f has the docstring, name, and argspec of f
    assert _f.__doc__ == "f documentation", "docstring preserved"
    assert 'x' in inspectcall.get_argspec(_f).args, "argspec preserved"
    # verify that calls to _f get redirected to f
    expected = 'x is 5'
    actual = f(5, None)
    assert actual == expected, "call redirected"
