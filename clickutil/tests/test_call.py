from ..argspec import get_argspec
from ..call import call


def test_call():
    def f(x, y):
        "f documentation"
        return 'x is {}'.format(x)

    @call(f)
    def _f(): pass

    # check that _f has the docstring, name, and argspec of f
    assert _f.__doc__ == "f documentation", "docstring preserved"
    assert 'x' in get_argspec(_f).args, "argspec preserved"
    # verify that calls to _f get redirected to f
    expected = 'x is 5'
    actual = f(5, None)
    assert actual == expected, "call redirected"
