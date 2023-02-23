FROM mysql:8.0

ARG MYSQL_ROOT_PASSWORD

COPY 01_create_db.sql /docker-entrypoint-initdb.d/01_create_db.sql
COPY 02_initial_data.sql /docker-entrypoint-initdb.d/02_initial_data.sql

ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
