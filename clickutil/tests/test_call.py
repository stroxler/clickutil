from ..argspec import get_argspec
from ..call import call, use_output


def test_call():
    def f(x, y):
        "f documentation"
        return 'x is {}'.format(x)

    @call(f)
    def _f(): pass

    # check that _f has the docstring, name, and argspec of f
    assert _f.__doc__ == "f documentation", "docstring preserved"
    assert 'x' in get_argspec(_f).args, "argspec preserved"
    assert _f.__name__ == "_f"
    # verify that calls to _f get redirected to f
    expected = 'x is 5'
    actual = _f(5, None)
    assert actual == expected, "call redirected"


def test_use_output():
    def f(x, y):
        "f documentation"
        return x + y

    outputs = []

    @use_output(f)
    def _f(output):
        outputs.append(output)

    # check that _f has the docstring, name, and argspec of f
    assert _f.__doc__ == "f documentation", "docstring preserved"
    assert 'x' in get_argspec(_f).args, "argspec preserved"
    assert _f.__name__ == "_f"
    # verify that calls to _f get redirected to f
    expected = 3
    actual = _f(1, 2)
    assert actual == expected, "call redirected"
    assert outputs == [expected, ], "output was sent to _f"
