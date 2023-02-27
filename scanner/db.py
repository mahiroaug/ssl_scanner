import os
import dataset


__all__ = ['db']


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


db = dataset.connect(_load_connection_string())
