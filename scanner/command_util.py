import typing
import click
from functools import wraps


def output_data(msg):
    """ Print line. """
    click.echo(msg)


def output_message(msg):
    """ Print a message line. """
    click.echo(click.style(msg, fg='green'))


def output_error(msg):
    """ Print an error message line. """
    click.echo(click.style(msg, fg='red'), err=True)


def handle_exception(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CommandException as e:
            click.echo(click.style(str(e), fg='red'))
            return e.exit_code
    return wrapper


class CommandException(Exception):

    def __init__(self, exit_code: int = 1, *args: object) -> None:
        super().__init__(*args)
        self.exit_code = exit_code

    @property
    def exit_code(self):
        return self._exit_code

    @exit_code.setter
    def exit_code(self, value):
        self._exit_code = value

    @classmethod
    def ProgramError(cls, point) -> 'CommandException':
        return cls(9, f"[FATAL] Run into the unexpected branch. point={point}")

    @classmethod
    def TableNotFound(cls) -> 'CommandException':
        return cls(2, "[FATAL] Database connection failure or 'Certificates' table not found")

    @classmethod
    def InvalidDataState(cls, domain: str) -> 'CommandException':
        return cls(4, f"[FATAL] Unexpected record state. '{domain}' is broken.")

    @classmethod
    def InvalidArgumentError(cls, msg: str) -> 'CommandException':
        return cls(3, f"[FATAL] Invalid argument. {msg}")

    @classmethod
    def InvalidDomainArgument(cls) -> 'CommandException':
        return cls.InvalidArgumentError("domain is malformed.")

