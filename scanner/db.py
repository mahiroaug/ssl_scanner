"""
This module provide a "dataset.Database" instance to communicate with a database.
The "dataset" library API documentation can be viewed at the following URL.

https://dataset.readthedocs.io/en/latest/api.html

    # The target database is determined by the "DATABASE" environment variable
    # when this module is loaded.
    from db import db

    # Get a "dataset.Table" instance to communicate with "Certificates" table.
    table = db.get_table("Certificates")
    # Count entries in "Certificates" table.
    table.count()

"DATABASE" or "MYSQL_PASSWORD" environment variables must be set to use this module.

    # Use SQLite3 database
    export DATABASE="sqlite:///db.sqlite"

    # Use MySQL (MariaDB) database.
    export DATABASE="mysql://user:password@host:port/dbname"

"""

import os
import dataset


__all__ = ['db', 'create_certificates_table', 'populate_certificates_table']


def _load_connection_string() -> str:
    """
    Build a database connection string from environment variables.
    The supported databases are depend on "dataset" library.

    Returns:
        str: A database connection string, like "schema://user:password@dbhost/dbname"
    """
    connection_string = os.environ.get('DATABASE')
    if connection_string is None:
        mysql_host = os.environ.get('MYSQL_HOST', 'DB')
        mysql_user = os.environ.get('MYSQL_USER', 'root')
        mysql_database = os.environ.get('MYSQL_DATABASE', 'Certificates')
        mysql_password = os.environ.get('MYSQL_PASSWORD', os.environ.get('MYSQL_ROOT_PASSWORD'))
        if mysql_password is None:
            connection_string = f"mysql://{mysql_user}@{mysql_host}/{mysql_database}"
        else:
            connection_string = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
    return connection_string


def create_certificates_table(drop_exists=False) -> dataset.Table:
    """
    Create 'Certificates' table on the database.

    The target database is determined at the time this module is loaded into the application.

    Args:
        drop_exists (bool, optional):
            If True, the existing table will be dropped and recreated.
            Defaults to False.

    Returns:
        dataset.Table: An instance to communicate with the table.
    """
    if db.has_table("Certificates") and drop_exists:
        db.get_table("Certificates").drop()
    table: dataset.Table = db.create_table("Certificates", primary_id="ID")
    table.create_column("Domain", type=db.types.string(256), unique=True)
    table.create_column("Subject", type=db.types.text)
    table.create_column("Issuer", type=db.types.text)
    table.create_column("SigAlgorithm", type=db.types.text)
    table.create_column("Valid_From", type=db.types.date)
    table.create_column("Valid_To", type=db.types.date)
    table.create_column("Last_Check", type=db.types.datetime)
    return table


def populate_certificates_table(domains: list):
    """
    Add entries into "Certificates" table.

    Args:
        domains (list): A list of "domain" strings to be inserted.
    """
    table = db.get_table("Certificates")
    table.insert_many([dict(Domain=d) for d in domains])


db = dataset.connect(_load_connection_string())
