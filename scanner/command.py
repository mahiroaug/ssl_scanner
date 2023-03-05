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


@cli.command()
@click.option("--drop", is_flag=True, default=False)
@handle_exception
def init(drop: bool):
    """ Create a table in the database

    Args:
        drop (bool): Drop existing table and re-create
    """
    from db import create_certificates_table
    create_certificates_table(drop)
    output_message("Init table: OK")


if __name__ == '__main__':
    cli()
