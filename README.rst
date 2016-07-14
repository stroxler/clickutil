clickutil - making click even better
====================================

Python's `click` package is an awesome tool for building command-line
interfaces. But sometimes to use `click` the way I want to I need a
lot of boilerplate code, so I wrote `clickutil` to make my command
line packages more concise and less buggy.


Keep access to your python functions by using `clickutil.call`
--------------------------------------------------------------

A normal click decorator looks something like this::

    @click.command('do-something')
    @click.option('--an-option', required=True, help='a click option')
    def do_something(an_option):
        click.echo(an_option)


This can be frustrating if you want to expose a public api that is accessible
from both python and the command line, because the original `do_someting`
function which took an argument is replaced by a function that takes no
arguments and reads `sys.argv` for inputs.

The `clickutil.call` decorator lets you instead decorate a placeholder function
as calling some function you want as part of your public api, so that the
original function may still be accessed from python::

    def do_something(an_option):
        click.echo(an_option)

    @click.command('do-something')
    @click.option('--an-option', required=True, help='a click option')
    @clickutil.call(do_something)
    def _do_something(): pass


Add debugging using clickutil.debug
-----------------------------------

A common workflow for python developers is to load code from `ipython` and run
it from the shell. There are several benefits to doing this, one of which is
that you can use the `%debug` magic command if unhandled exceptions occur.

The `clickutils.debug` decorator lets you get a similar benefit when running
click commands, by dropping into a debugger on unhandled exceptions. By default
it adds an option `--debug`. When that flag is used, on any exceptions the click
endpoint will enter a debugger after delaying a few seconds (which gives the
user a chance to keyboard escape if they don't need to debug). The delay, and
also whether to debug by default, can both be configured.

By default, `clickutil` will first try `pudb` and then `pdb` for debugging, but
this is configurable via an argument.

For example, here we debug using `ipdb` after 10 seconds of waiting in the
event that `do_something` raises an exception. We do so by default, so to
turn off this behavior you would need to use the `--no-debug` flag::

  import ipdb

  @click.command('do-something')
  @clickutil.debug(default=False, delay=10, use_debugger=ipdb)
  @clickutil.call(do_something)
  def _do_something(): pass

More concise options and flags
------------------------------

The `click.option` function takes a lot of arguments to control different
kinds of behaviors, and conflates a lot of different kinds of options
(for example, boolean flags like `--debug/--no-debug` get grouped together
with options that take arguments). Partly because the behavior of a click
option depends on many different arguments, some of the default behaviors -- such
as not showing the default value of an option that has a default in the
`--help` output -- don't make sense.

To make working with options easier, `clickutil` provides three more specific
functions: `clickutil.boolean_flag` for setting flags such as `--debug`,
`clickutil.required_option` for options that take an argument and must be
provided, and `clickutil.default_option` for options that take an argument
and need not be provided. It also provides three special option types,
`clickutil.EXISTING_FILE`, `clickutil.EXISTING_DIR`, and
`clickutil.NEW_FILE_OR_DIR`, to handle the most common `click.Path` input
types.

Detecting default values from function signatures
-------------------------------------------------

Because clickutil tries to keep the original python function available
for calling from python using `clickutil.call`, it becomes irritating to
have to set default values for `default_option`s and `boolean_flag`s twice,
both in the function and in the click decorators. In addition, the fact that
these two can differ becomes a potential source of bugs.

By inspecing the arguments of functions, `clickutil` is able to set defaults
based on the argument list in the definition of a function.

The `clickutil.boolean` decorator is similar to `clickutil.boolean_flag`,
except it picks up its default value from the function signature. Similarly,
`clickutil.option` is like `clickutil.required_option` or
`clickutil.default_option`, depending on whether there's a default value in the
function signature.
