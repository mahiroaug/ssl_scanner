import validators
import json
import dataset
import typing
import click
import re
import io
from datetime import date, datetime
import ssl_certificate_checker
import controler
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


@click.argument("domain")
@handle_exception
def add(domain: str):
    """ Register a new domain into the database.

    Args:
        domain (str): A domain name to register
    """
    assert_domain_format(domain)
    table = get_table()
    row = table.find_one(Domain=domain)
    if row is not None:
        output_error(f"Domain {domain} is already registered.")
        return 1
    table.insert({"Domain": domain})
    output_message(f"Domain {domain} inserted.")


@cli.command()
@click.argument("domain")
@handle_exception
def delete(domain: str):
    """ Delete one domain record from the database

    Args:
        domain (str): A domain name to delete
    """
    assert_domain_format(domain)
    table = get_table()
    row = table.find_one(Domain=domain)
    if row is None:
        output_error(f"Domain {domain} not registered.")
        return 1
    table.delete(Domain=domain)
    output_message(f"Domain {domain} deleted.")


@cli.command()
@click.argument("domain")
@handle_exception
def scan(domain: str):
    """ Scan domains over HTTPS, and update informations in the database

    Args:
        domain (str): A domain to scan
    """
    assert_domain_format(domain)
    table = get_table()
    row = table.find_one(Domain=domain)
    if row is None:
        output_error(f"Domain {domain} not registered.")
        return 1
    scan_result = ssl_certificate_checker.scan(domain)
    if scan_result:
        controler.update(domain, *scan_result)
    row = table.find_one(Domain=domain)
    output_multiple_data([row])


@cli.command()
@click.option("-a", "--allocate", type=str, required=True,
              help="Task allocate group, formed like '1/2'. "
                   "This means 'Theres 2 workers and this is the 1st worker process'. ")
@handle_exception
def bulkscan(allocate: str):
    """ Scan a part of all domains and update information, in the database.
    You must specify '--allocate 1/3' option, to tell the process about an allocated domains.
    If you will start 3 bulkscan processes, the first process's option is '--allocate 1/3' and the second is '--allocate 2/3'.
    """
    (worker_id, workers) = parse_allocate_argument(allocate)
    controler.main(workers=workers, worker_id=worker_id)


@cli.command()
@click.argument('input', type=click.File('r'))
@click.option("-d", "--delete", is_flag=True, default=False,
              help="If true, domains that are not listed in the file will be deleted from the database.")
@click.option("-y", "--yes", is_flag=True, default=False,
              help="If true, Skip prompts.")
@handle_exception
def load(input: io.TextIOWrapper, delete: bool, yes: bool):
    """ Sync database records with the domain list file.

    Args:
        input (io.TextIOWrapper): Simple domain list file.
        delete (bool): If true, domains that are not listed in the file will be deleted from the database.
        yes (bool): If true, Skip prompts.
    """
    # Input domain list.
    listed_domains = set(load_domains_list(input))
    # Current domain list.
    table = get_table()
    exists_domains = set([r['Domain'] for r in table.all()])

    # Check Changes
    add_change = listed_domains - exists_domains
    del_change = exists_domains - listed_domains
    
    if len(add_change) == 0 and len(del_change) == 0:
        output_message("There is nothing to be updated.")
        return 0

    if len(add_change) > 0:
        output_message("[Domains to be ADDED]:")
        output_message(" " + ", ".join(add_change))
    if delete and len(del_change) > 0:
        output_error("[Domains to be DELETED]")
        output_error(" " + ", ".join(del_change))
    if not yes:
        click.confirm('Do you want to continue?', abort=True)

    table.insert_many([{"Domain": domain} for domain in add_change])
    output_message(f"{len(add_change)} domains inserted.")
    if delete and len(del_change) > 0:
        print([q for q in table.find(Domain=del_change)])
        table.delete(Domain=del_change)
        output_error(f"{len(del_change)} domains deleted.")


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


def parse_allocate_argument(allocate_argument: str) -> typing.Tuple[int, int]:
    match = re.match(r'^([1-9][0-9]*)/([1-9][0-9]*)$', allocate_argument)
    if not match:
        raise CommandException.InvalidAllocateArgument()
    worker = int(match.group(1))
    tasks = int(match.group(2))
    if worker > tasks:
        raise CommandException.InvalidAllocateArgument()
    return (worker, tasks)


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


# File IO
def load_domains_list(file: io.TextIOWrapper) -> list[str]:
    listed_domains = []
    for line in file.readlines():
        m = re.search(r'^\s*([^ ]+?)(\s*#.*)?$', line)
        if m is None:
            continue
        value = m.group(1)
        if len(value) == 0:
            continue
        assert_domain_format(value)
        listed_domains.append(value)
    return listed_domains


if __name__ == '__main__':
    cli()
