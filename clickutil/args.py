import inspect
import click

from .wrapping import update_wrapper


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
        click_decorator =  click.option(flag,
                                        type=type, default=default,
                                        help=help, show_default=True)
    else:
        click_decorator = click.option(flag, short_flag,
                                       type=type, default=default,
                                       help=help, show_default=True)
    def decorator(f):
        wrapper = click_decorator(f)
        update_wrapper(wrapper, f)
        return wrapper

    return decorator


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

    return _mk_decorator(click_decorator)


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
    return _mk_decorator(click_decorator)


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
            return required_option(flag, short_flag, type, default, help)(f)

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
        return boolean_flag(flag, type, default, help)(f)

    return decorator


def _mk_decorator(click_decorator):
    """
    Add a call to wrapping.update_wrapper to the output of a click decorator,
    in order to persist extra metadata.

    """
    def decorator(f):
        wrapper = click_decorator(f)
        update_wrapper(wrapper, f)
        return wrapper
    return decorator


def get_arg_default(f, varname):
    """
    Return a (bool, object) tuple, where the first element indicates
    whether the variable with name `varname` has a default value in calls
    to `f`. The second entry is None if not, and otherwise is the default
    value.

    In order to use this function, the function must have an
    __argspec__ field, whose value should be the output of
    `inspect.getargspec` on the original function (functools.update_wrapper
    does *not* persist the data inspect uses). The most common case of this
    is when clickutil.call is used for the bottom decorator, and all
    of the decorators betweent he active decorator and the clickutil.call
    decorator are clickutil decorators (which preserve __argspec__)

    """
    f_args = f.__argspec__
    if varname not in f_args.args:
        if f_args.keywords is None:
            raise ValueError('Variable %r not found in spec of func %s'
                             % (varname, f.__name__))
        return (False, None)
    # args and defaults of an argspec are both in the order given. Since
    # we don't really care about the order, the easiest way to line them
    # up is to reverse them
    varidx = f_args.args[::-1].index(varname)
    if varidx < len(f_args.defaults):
        return (True, f_args.defaults[::-1][varidx])
    else:
        return (False, None)
