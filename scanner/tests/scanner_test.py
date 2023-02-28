import os
import dataset
import pytest
from datetime import datetime, date

os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
os.environ["DATABASE"] = "sqlite:///test.sqlite"

from db import db, create_certificates_table, populate_certificates_table
from controler import get_record_count, get_record_chunk, get_list, update


@pytest.fixture()
def table():
    table = create_certificates_table(drop_exists=True)
    print(table)
    print(table.columns)
    populate_certificates_table([
        "github.com",
        "slack.com",
        "google.com",
        "yahoo.com",
        ])
    print(table.columns)
    print(table.find())
    return table


def test_initdb(table):
    assert table.count() == 4


def test_get_record_count():
    count = get_record_count()
    assert count == 4


def test_get_record_chunk_s1():
    domains = get_record_chunk(1, 1)
    assert domains == ["github.com"]

def test_get_record_chunk_s2():
    domains = get_record_chunk(1, 2)
    assert domains == ["github.com", "slack.com"]

def test_get_record_chunk_s2():
    domains = get_record_chunk(2, 3)
    assert domains == ["slack.com", "google.com"]


def test_get_list_s1():
    domains = get_list(3, 1)
    assert domains == ["github.com", "slack.com"]

def test_get_list_s2():
    domains = get_list(3, 2)
    assert domains == ["google.com"]

def test_get_list_s3():
    domains = get_list(3, 3)
    assert domains == ["yahoo.com"]

def test_update_s1(table: dataset.Table):
    before = table.find_one(Domain="github.com")
    default_data = [
        1,
        "github.com",
        None,
        None,
        None,
        None,
        None,
        None,
    ]
    assert [v for v in before.values()] == default_data
    data = [
        "github.com",
        "www.github.com",
        "Test CA",
        "RSA 256",
        date.fromisoformat("2023-01-01"),
        date.fromisoformat("2023-01-02"),
        datetime.fromisoformat("2023-01-03 00:00:00"),
    ]
    inserted = update(*data)
    after = table.find_one(Domain="github.com")

    assert [v for v in inserted.values()] == [*data]
    assert [v for v in after.values()] == [1, *data]
