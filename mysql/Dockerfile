FROM mysql:8.0

COPY 01_create_db.sql /docker-entrypoint-initdb.d/01_create_db.sql
COPY 02_initial_data.sql /docker-entrypoint-initdb.d/02_initial_data.sql
