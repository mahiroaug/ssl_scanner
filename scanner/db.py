import os
import dataset


__all__ = ['db', 'format_table', 'populate_table']


def _load_connection_string():
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
    if db.has_table("Certificates") and drop_exists:
        db.get_table("Certificates").drop()
    table: dataset.Table = db.create_table("Certificates", primary_id="ID", primary_increment="ID")
    table.create_column("Domain", type=db.types.text, unique=True)
    table.create_column("Subject", type=db.types.text)
    table.create_column("Issuer", type=db.types.text)
    table.create_column("SigAlgorithm", type=db.types.text)
    table.create_column("Valid_From", type=db.types.date)
    table.create_column("Valid_To", type=db.types.date)
    table.create_column("Last_Check", type=db.types.datetime)
    return table


def populate_certificates_table(domains: list):
    table = db.get_table("Certificates")
    table.insert_many([dict(Domain=d) for d in domains])


db = dataset.connect(_load_connection_string())
