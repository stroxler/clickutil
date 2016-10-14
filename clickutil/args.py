import click

from .argspec import get_argspec
from .util import mk_decorator


EXISTING_FILE = click.Path(exists=True, dir_okay=False, file_okay=True)
EXISTING_DIR = click.Path(exists=True, dir_okay=True, file_okay=False)
NEW_FILE_OR_DIR = click.Path(exists=False)


def default_option(flag, short_flag, type, default, help):
    """
    Consistent interface for creating click options with defaults.

    PARAMETERS
    ----------
    flag: str
    short_flag: {str, None}
    type: any click arg type
    default: object
    help: str
    """
    if short_flag is None:
        click_decorator = click.option(flag,
                                       type=type, default=default,
                                       help=help, show_default=True)
    else:
        click_decorator = click.option(flag, short_flag,
                                       type=type, default=default,
                                       help=help, show_default=True)

    return mk_decorator(click_decorator)


def required_option(flag, short_flag, type, help):
    """
    Consistent interface for creating click options without defaults.

    PARAMETERS
    ----------
    flag: str
    short_flag: {str, None}
    type: any click arg type
    help: str
    """
    if short_flag is None:
        click_decorator = click.option(flag,
                                       type=type, required=True,
                                       help=help, show_default=True)
    else:
        click_decorator = click.option(flag, short_flag,
                                       type=type, required=True,
                                       help=help, show_default=True)

    return mk_decorator(click_decorator)


def boolean_flag(flag, default, help):
    """
    Consistent interface for creating boolean flags using click.


    PARAMETERS
    ----------
    flag: str
    default: boolean
    help: str
    """
    if not flag.startswith('--'):
        raise ValueError('flag {} does not start with "--"'.format(flag))
    stripped_flag = flag[2:]
    click_flag = '--{0}/--no-{0}'.format(stripped_flag)
    click_decorator = click.option(click_flag, default=default, help=help,
                                   show_default=True)
    return mk_decorator(click_decorator)


def option(flag, short_flag, type, help):
    """
    Automagically detect whether a function has a default value for an
    option, and add an appropriately defaulted or required option
    decorator.

    This can only be used if you have wrapped the function
    in `clickutil.call.call`, since normally decorators strip out the
    information we need here.

    Note that if you want to provide default values for arguments only
    when calling from the command line, but not from python, then you
    must use `default_option` instead.

    For the sake of flexibility, we do not check the default value's
    type against the declared type.

    """
    varname = flag.strip('-').replace('-', '_')

    def decorator(f):
        has_default, default = get_arg_default(f, varname)
        if has_default:
            return default_option(flag, short_flag, type, default, help)(f)
        else:
            return required_option(flag, short_flag, type, help)(f)

    return decorator


def boolean(flag, help):
    """
    Automagically detect the default value for a boolean flag, and
    and an appropriate decorator.

    This can only be used if you have wrapped the function
    in `clickutil.call.call`, since normally decorators strip out the
    information we need here.

    Note that if you want to provide a default for the flag on the
    command line but make it required in python calls, you must use
    `boolean_flag` instead.

    """
    varname = flag.strip('-').replace('-', '_')

    def decorator(f):
        has_default, default = get_arg_default(f, varname)
        if not has_default:
            raise ValueError('Attempting to declare boolean with '
                             'auto-default, but variable %r is not a kwarg'
                             % varname)
        if default not in (True, False):
            raise ValueError('Default value %r for variable %r is not boolean'
                             % (default, varname))
        return boolean_flag(flag, default, help)(f)

    return decorator


def get_arg_default(f, varname):
    """
    Return a (bool, object) tuple, where the first element indicates
    whether the variable with name `varname` has a default value in calls
    to `f`, and the second entry has the default if there is one.

    PARAMETERS
    ----------
    f : function
        A function. In order for this to work properly, the output
        of `argspec.get_argspec(f)` needs include the variable you
        are looking for. This will be true if `f` is a raw function, or
        the output of any `clickutil` or `wrapt` decorator.
        But many third-party decorators, including those from `click`,
        clobber the required metadata.
    varname : str
        A variable name. Must be one of the regular arguments of `f` (not
        varargs or packed keywordargs), or else `f` must take a packed
        keyword argument. In the latter case, we treat all arguments which
        don't correspond to regular arguments as having no default value.

    RETURNS
    -------
    (has_default, default): tuple of (boolean, object)
        The first entry indicates whether `varname` has a default
        value in the signature of `f`, and the second is the default
        value if so, otherwise None.

    """
    f_argspec = get_argspec(f)
    if varname not in f_argspec.args:
        if f_argspec.keywords is None:
            raise ValueError('Variable %r not found in spec of func %s'
                             % (varname, f.__name__))
        return (False, None)
    # args and defaults of an argspec are both in the order given. Since
    # we don't really care about the order, the easiest way to line them
    # up is to reverse them
    if f_argspec.defaults is None:
        return (False, None)
    varidx = f_argspec.args[::-1].index(varname)
    if varidx < len(f_argspec.defaults):
        return (True, f_argspec.defaults[::-1][varidx])
    else:
        return (False, None)
