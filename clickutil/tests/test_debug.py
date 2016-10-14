from __future__ import print_function

import click
from click.testing import CliRunner

from ..argspec import get_argspec
from ..debug import debug


class MockDebugger(object):
    def __init__(self):
        self.called = False

    def post_mortem(self, tb):
        self.called = True


def test_debug_preserves_metadata():

    @debug(False, delay=0)
    def f(x=3):
        "f documentation"
        pass

    assert f.__doc__ == "f documentation"
    assert 'x' in get_argspec(f).args


def test_debug_not_called_if_no_error():

    mock_debugger = MockDebugger()

    runner = CliRunner()

    @click.command('f')
    @debug(True, delay=0, use_debugger=mock_debugger)
    def f(x=3):
        click.echo('x = %s' % x)

    result = runner.invoke(f)
    assert result.output.strip() == 'x = 3'
    assert result.exception is None
    assert not mock_debugger.called


def test_debug_not_called_by_default():

    mock_debugger = MockDebugger()
    runner = CliRunner()

    @click.command('f')
    @debug(False, delay=0, use_debugger=mock_debugger)
    def f(x=3):
        raise ValueError("an error")

    result = runner.invoke(f)
    assert result.exception is not None
    assert not mock_debugger.called


def test_debug_called_if_debug():

    mock_debugger = MockDebugger()
    runner = CliRunner()

    @click.command('f')
    @debug(False, delay=0, use_debugger=mock_debugger)
    def f(x=3):
        raise ValueError("an error")

    runner.invoke(f, ['--debug'])
    assert mock_debugger.called


def test_debug_not_called_if_no_debug():

    mock_debugger = MockDebugger()
    runner = CliRunner()

    @click.command('f')
    @debug(True, delay=0, use_debugger=mock_debugger)
    def f(x=3):
        raise ValueError("an error")

    result = runner.invoke(f, ['--no-debug'])
    assert result.exception is not None
    assert not mock_debugger.called


def test_debug_called_by_default():

    mock_debugger = MockDebugger()
    runner = CliRunner()

    @click.command('f')
    @debug(True, delay=0, use_debugger=mock_debugger)
    def f(x=3):
        raise ValueError("an error")

    runner.invoke(f)
    assert mock_debugger.called
