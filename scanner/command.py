import validators
import json
import dataset
import typing
import click
import re
from datetime import date, datetime
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


@cli.command('list')
@click.option('-o', '--output', type=click.Choice(['line', 'json']), default='line')
@click.option('-s', '--sort', type=click.Choice(['id', 'expire', 'scan']), default='id')
@handle_exception
def list_(output, sort):
    """ List domain records in the database
    """
    table = get_table()
    order_by_keys = {'id': ['ID'],
                     'expire': ['Valid_To'],
                     'scan': ['Last_Check'],
                     }
    rows = [row for row in table.find(order_by=order_by_keys[sort])]
    if len(rows) > 0:
        output_multiple_data(rows, format=output)
    else:
        output_error('No records found.')


@cli.command()
@click.argument("domain")
@click.option('-o', '--output', type=click.Choice(['line', 'json']), default='line')
@handle_exception
def show(domain: str, output: str):
    """ Show one domain record in the database

    Args:
        domain (str): A domain name to show
    """
    assert_domain_format(domain)
    table = get_table()
    row = table.find_one(Domain=domain)
    if row is None:
        output_error(f"Domain {domain} not registered.")
        return 1
    else:
        output_single_data(row, format=output)



# Functions

def get_table() -> dataset.Table:
    """ Get dataset instance of 'Certificates' table. """
    from db import db
    if not db.has_table('Certificates'):
        raise CommandException.TableNotFound()
    return db.get_table("Certificates")


def assert_domain_format(domain: str):
    """ Domain format assertion """
    result = validators.domain(domain)  # type: ignore
    if isinstance(result, validators.utils.ValidationFailure):
        raise CommandException.InvalidDomainArgument()


def convert_to_output(row: dict, now: date) -> dict:
    """ Organize data fields for output.

    Args:
        row (dict): Data to organize, that is a row in the "Certificates" table.
        now (date): A base date to calculate the day of expire the certificate.

    Returns:
        dict: Data to display.
    """
    keys = [
        'ID',
        'Domain',
        'Subject',
        'Issuer',
        'SigAlgorithm',
        'Valid_From',
        'Valid_To',
        'Last_Check'
    ]
    if row['Valid_To'] is None:
        remain = None
    else:
        remain = (row['Valid_To'] - now).days
    data = {k: row[k] for k in keys}
    data['Remaining_Days'] = remain
    data['Remaining_Base'] = now

    result = serialize_field(data)
    if isinstance(result, dict):
        return result
    else:
        raise CommandException.ProgramError('non-dict-organize')


def serialize_field(obj) -> typing.Union[list, dict, str, int, None]:
    """ Extra serialization code of json.dumps. """
    if obj is None:
        return None
    elif isinstance(obj, (str, int)):
        return obj
    elif isinstance(obj, list):
        return [serialize_field(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: serialize_field(v) for k, v in obj.items()}
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat() + "Z"
    raise TypeError(f"Object of type {type(obj)} is not serializable")


def lines_dumps(rows: list[dict] | dict) -> str:
    """ Convert data to str in line format.

    Args:
        rows (list[dict] | dict): Record data, converted by 'convert_to_output' function.

    Returns:
        str: Line format string.
    """
    layout = "{id}: {domain}\texpire_on:{until} ({remain}), checked_at:{checked_at}"
    if isinstance(rows, dict):
        rows = [rows]
    lines = []
    for row in rows:
        if row['Remaining_Days'] is None:
            remain_days = '-- days'
        else:
            remain_days = f"{row['Remaining_Days']} days"

        data = {'id': row['ID'],
                'domain': row['Domain'],
                'until': row['Valid_To'],
                'remain': remain_days,
                'checked_at': row['Last_Check'],
                }
        line = layout.format(**data)
        lines.append(line)
    return "\n".join(lines)


# Output STDIO
def output_single_data(row: dict, format="line"):
    """ Print a database entry in specified format to stdout. """
    now = date.today()
    data = convert_to_output(row, now)
    if format == 'line':
        output_data(lines_dumps(data))
    elif format == 'json':
        output_data(json.dumps(data, default=serialize_field))
    else:
        raise CommandException.ProgramError('unknown-format')


def output_multiple_data(rows: list[dict], format="line"):
    """ Print database entries in JSON format. """
    now = date.today()
    data = [convert_to_output(row, now) for row in rows]

    if format == 'line':
        output_data(lines_dumps(data))
    elif format == 'json':
        output_data(json.dumps(data, default=serialize_field))
    else:
        raise CommandException.ProgramError('unknown-format')


if __name__ == '__main__':
    cli()
