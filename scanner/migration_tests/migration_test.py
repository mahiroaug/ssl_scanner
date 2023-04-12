import os
import pytest
import click
from datetime import datetime, date
from click.testing import CliRunner, Result

# Overwrite database connecting options for tests
os.environ["DATABASE"] = "sqlite:///test.sqlite"
# Supress warnings about SQLAlchemy
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
import dataset  # noqa: E402


@pytest.fixture(scope='module')
def db_v1():
    from migration_tests.extra.db_v1 import db as db_v1
    return db_v1


@pytest.fixture(scope='module')
def table_v1(db_v1: dataset.Table) -> dataset.Table:
    """ Create 'Certificates' table in previous version on the database
    """
    from migration_tests.extra import db_v1
    table = db_v1.create_certificates_table(drop_exists=True)
    db_v1.populate_certificates_table([
        "github.com",
        "slack.com",
        "google.com",
        "yahoo.com",
    ])
    data = [
        "github.com",
        "www.github.com",
        "Test CA",
        "RSA 256",
        date.fromisoformat("2023-01-01"),
        date.fromisoformat("2023-01-02"),
        datetime.fromisoformat("2023-01-03 00:00:00"),
    ]
    inserted = update_v1(db_v1.db, *data)
    after = table.find_one(Domain="github.com")
    assert [v for v in inserted.values()] == [*data]
    assert [v for v in after.values()] == [1, *data]
    return table


@pytest.fixture(scope='module')
def db(table_v1: dataset.Table):
    from db import db
    return db


@pytest.fixture(scope='module')
def table(table_v1: dataset.Table):
    print(table_v1.columns)
    from db import create_certificates_table
    table = create_certificates_table(drop_exists=False)

    assert table.count() == 4

    check_data = dict(
        ID=1,
        Domain="github.com",
        Subject="www.github.com",
        Issuer="Test CA",
        SigAlgorithm="RSA 256",
        Valid_From=date.fromisoformat("2023-01-01"),
        Valid_To=date.fromisoformat("2023-01-02"),
        Last_Check=datetime.fromisoformat("2023-01-03 00:00:00"),
        CertSerial=None,
    )
    migrated_data = table.find_one(Domain="github.com")
    assert all([v == migrated_data[k] for k, v in check_data.items()])
    return table


@pytest.fixture(name='cli')
def cli(table: dataset.Table) -> click.Group:
    from command import cli as cli_application
    return cli_application


def test_update_s1(table: dataset.Table):
    from controler import update  # noqa:E402

    data = dict(
        Domain="slack.com",
        Subject="www.slack.com",
        Issuer="Test CA",
        SigAlgorithm="RSA 256",
        Valid_From=date.fromisoformat("2023-01-01"),
        Valid_To=date.fromisoformat("2023-01-02"),
        Last_Check=datetime.fromisoformat("2023-01-03 00:00:00"),
        CertSerial="012345",
    )
    inserted = update(*data.values())
    after = table.find_one(Domain="slack.com")
    assert [v for v in inserted.values()] == [*data.values()]
    assert all([v == after[k] for k, v in data.items()])


def update_v1(db_v1, domain, subject, issuer, sig_algo, start_date, expiry_date, checkdate):
    data = dict(
        Domain=domain,
        Subject=subject,
        Issuer=issuer,
        SigAlgorithm=sig_algo,
        Valid_From=start_date,
        Valid_To=expiry_date,
        Last_Check=checkdate,
    )
    with db_v1 as tx:
        certificates = tx["Certificates"]
        certificates.update(data, ["Domain"])
    return data


def test_info(cli: click.Group):
    result: Result = CliRunner().invoke(cli=cli, args=['info'])
    assert result.exit_code == 0
    assert result.stdout.strip() == os.environ["DATABASE"]


def test_list(cli: click.Group):
    result: Result = CliRunner().invoke(cli=cli, args=['list'])
    assert result.exit_code == 0
    output = result.stdout.splitlines()
    assert len(output) == 4


def test_show(cli: click.Group):
    result: Result = CliRunner().invoke(cli=cli, args=['show', 'github.com'])
    assert result.exit_code == 0
    output = result.stdout.splitlines()
    assert len(output) == 1
