import click


def command(parent):
    if parent is None:
        parent = click

    def decorator(f):
        command_name = f.__name__.strip('_').replace('_', '-')
        return parent.command(command_name)(f)

    return decorator
