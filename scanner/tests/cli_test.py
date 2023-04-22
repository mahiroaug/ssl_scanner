import os
import pytest
import click
from click.testing import CliRunner, Result

# Overwrite database connecting options for tests
os.environ["DATABASE"] = "sqlite:///test.sqlite"
# Supress warnings about SQLAlchemy
os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
import dataset  # noqa: E402


@pytest.fixture(scope="module")
def db():
    from db import db
    return db


@pytest.fixture(scope="module")
def table(db: dataset.Database):
    from db import create_certificates_table, populate_certificates_table
    table = create_certificates_table(drop_exists=True)
    populate_certificates_table([
        "github.com",
        "slack.com",
        "google.com",
        "yahoo.com",
    ])
    return table


@pytest.fixture(name='cli', scope="module")
def cli(db: dataset.Database) -> click.Group:
    from command import cli as cli_application
    return cli_application


def test_initdb(table: dataset.Table):
    assert table.count() == 4


def test_info(cli: click.Group):
    result: Result = CliRunner().invoke(cli=cli, args=['info'])
    assert result.exit_code == 0
    assert result.stdout.strip() == os.environ["DATABASE"]


def test_list(cli: click.Group):
    result: Result = CliRunner().invoke(cli=cli, args=['list'])
    assert result.exit_code == 0
    output = result.stdout.splitlines()
    assert len(output) == 4
    expect = "\n".join([
        "1: github.com\texpire_on:None (-- days), checked_at:None",
        "2: slack.com\texpire_on:None (-- days), checked_at:None",
        "3: google.com\texpire_on:None (-- days), checked_at:None",
        "4: yahoo.com\texpire_on:None (-- days), checked_at:None",
    ])
    assert expect == result.stdout.strip()


def test_show(cli: click.Group):
    result: Result = CliRunner().invoke(cli=cli, args=['show', 'github.com'])
    assert result.exit_code == 0
    output = result.stdout.splitlines()
    assert len(output) == 1
    expect = "1: github.com\texpire_on:None (-- days), checked_at:None"
    assert result.stdout.strip() == expect
