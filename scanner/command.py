import click
from command_util import \
    CommandException, \
    output_data, \
    output_error, \
    output_message, \
    handle_exception


@click.group()
def cli():
    pass


@cli.command()
@handle_exception
def info():
    """ Show database info """
    from db import db
    url = db.engine.url
    output_message(url.render_as_string(hide_password=True))


if __name__ == '__main__':
    cli()
