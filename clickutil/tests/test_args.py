from __future__ import print_function

import pytest
import click
from click.testing import CliRunner

from ..args import (
    required_option,
    default_option,
    boolean_flag,
    option,
    boolean,
    get_arg_default,
)


def test_boolean_flag():

    runner = CliRunner()

    def run_suite(default_value):
        @click.command()
        @boolean_flag('--my-flag', default_value,
                      help="a click flag")
        def f(my_flag):
            if my_flag:
                print("yes")
            else:
                print("no")

        # help should show up
        result = runner.invoke(f, ['--help'])
        assert 'a click flag' in result.output

        # should default properly
        result = runner.invoke(f)
        assert result.exception is None
        assert result.output.strip() == 'yes' if default_value else 'no'

        # should take explicit True
        result = runner.invoke(f, ['--my-flag'])
        assert result.exception is None
        assert result.output.strip() == 'yes'

        # should take explicit False
        result = runner.invoke(f, ['--no-my-flag'])
        assert result.exception is None
        assert result.output.strip() == 'no'

    run_suite(True)
    run_suite(False)


def test_get_arg_default():

    def f(x, y=3): pass

    # test that it raises if there's an unknown arg
    # and no packed keyword args
    with pytest.raises(ValueError):
        get_arg_default(f, 'z')

    # check an argument with no default
    actual = get_arg_default(f, 'x')
    expected = (False, None)
    assert actual == expected

    # check an argument with a default
    actual = get_arg_default(f, 'y')
    expected = (True, 3)
    assert actual == expected

    # check that keyword args get no default
    def fprime(**kwargs): pass
    actual = get_arg_default(f, 'x')
    expected = (False, None)
    assert actual == expected

    # check that everything works if there are no default values
    # (prior to this test, there was a bug where no defaults led to
    #  calling len() on None)
    def f(x): pass
    actual = get_arg_default(f, 'x')
    expected = (False, None)
    assert actual == expected


def test_boolean():

    runner = CliRunner()

    def run_suite(default_value):

        @click.command()
        @boolean('--my-flag', 'a click flag')
        def f(my_flag=default_value):
            if my_flag:
                print("yes")
            else:
                print("no")

        # help should show up
        result = runner.invoke(f, ['--help'])
        assert 'a click flag' in result.output

        # should default properly
        result = runner.invoke(f)
        assert result.exception is None
        assert result.output.strip() == 'yes' if default_value else 'no'

        # should take explicit True
        result = runner.invoke(f, ['--my-flag'])
        assert result.exception is None
        assert result.output.strip() == 'yes'

        # should take explicit False
        result = runner.invoke(f, ['--no-my-flag'])
        assert result.exception is None
        assert result.output.strip() == 'no'

    run_suite(True)
    run_suite(False)

    # boolean flags with no default should be illegal
    with pytest.raises(ValueError):
        @click.command()
        @boolean('--my-flag', 'a flag')
        def f_no_default(my_flag):
            pass

    # non-boolean default values should be illegal
    with pytest.raises(ValueError):
        @click.command()
        @boolean('--my-flag', 'a flag')
        def f_non_boolean_default(my_flag='not_a_boolean'):
            pass


def run_required_option_suite(f):
    """
    Run tests for a required option with:
       option flag --my-option
       short flag -mo
       integer type
       help of 'a click option'

    Assume the function prints out the option value
    """

    runner = CliRunner()

    # help should show up
    result = runner.invoke(f, ['--help'])
    assert 'a click option' in result.output

    # should be required
    result = runner.invoke(f)
    assert result.exception is not None
    assert result.output.startswith('Usage:')

    # should only accept integers
    result = runner.invoke(f, 'not_an_integer')
    assert result.exception is not None
    assert result.output.startswith('Usage:')

    # should work with long flag
    result = runner.invoke(f, ['--my-option', '3'])
    assert result.exception is None
    assert result.output.strip() == '3'

    # should work with short flag
    result = runner.invoke(f, ['-mo', '3'])
    assert result.exception is None
    assert result.output.strip() == '3'


def test_required_option():

    @click.command()
    @required_option('--my-option', '-mo', int,
                     help="a click option")
    def f(my_option):
        print(my_option)

    run_required_option_suite(f)


def test_option_like_required_option_if_no_default():

    @click.command()
    @option('--my-option', '-mo', int, 'a click option')
    def f(my_option):
        print(my_option)

    run_required_option_suite(f)


def run_default_option_test_suite(f):
    """
    Run tests for a default option with:
       option flag --my-option
       short flag -mo
       integer type
       default value 42
       help of 'a click option'

    Assume the function prints out the option value
    """
    runner = CliRunner()

    # help should show up
    result = runner.invoke(f, ['--help'])
    assert 'a click option' in result.output

    # should only accept integers
    result = runner.invoke(f, 'not_an_integer')
    assert result.exception is not None
    assert result.output.startswith('Usage:')

    # should only accept integers
    result = runner.invoke(f, 'not_an_integer')
    assert result.exception is not None
    assert result.output.startswith('Usage:')

    # default value should work
    result = runner.invoke(f)
    assert result.exception is None
    assert result.output.strip() == '42'

    # should work with long flag
    result = runner.invoke(f, ['--my-option', '3'])
    assert result.exception is None
    assert result.output.strip() == '3'

    # should work with short flag
    result = runner.invoke(f, ['-mo', '3'])
    assert result.exception is None
    assert result.output.strip() == '3'


def test_default_option():

    @click.command()
    @default_option('--my-option', '-mo', int,
                    default=42,
                    help="a click option")
    def f(my_option):
        print(my_option)

    run_default_option_test_suite(f)


def test_option_like_default_option_if_default():

    @click.command()
    @option('--my-option', '-mo', int, "a click option")
    def f(my_option=42):
        print(my_option)

    run_default_option_test_suite(f)
