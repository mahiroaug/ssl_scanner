# ssl_scanner
Analyzing SSL certificates for a website.

# How To Use

## Create envifonment file
 - `mysql/env_mysql.env`
  ```
  MYSQL_ROOT_PASSWORD=
  TZ=Tokyo/Asia
  ```
 - `monitor/env_monitor.env`
  ```
  MYSQL_ROOT_PASSWORD=
  TZ=Tokyo/Asia
  SLACK_BOT_TOKEN=
  SLACK_CHANNEL_ID=
  ```
 - `scanner/env_scanner.env`
  ```
  MYSQL_ROOT_PASSWORD=
  TZ=Tokyo/Asia
  ```

## Make CSV file (a list of FQDNs to be surveyed)
 - `mysql/FQDN.csv`
  ```
  example1.com
  example2.com
  example3.com
  ```


## build & run
### config check
`docker compose config`

### build
`docker compose --profile extra build --no-cache`

### run (deploy DB server)
`docker compose up -d`


### run (scanner by cli or cronjob)
`docker compose run doc-scanner controler.py <nodes> <node_id>`

- `nodes` is a line of parallels.
- `node_id` is each node.

example:
- `docker compose run doc-scanner controler.py 4 1`
- `docker compose run doc-scanner controler.py 4 2`
- `docker compose run doc-scanner controler.py 4 3`
- `docker compose run doc-scanner controler.py 4 4`

in parallel:

- `seq 1 4 | parallel docker compose run doc-scanner controler.py 4 {}`

### post message in slack
`docker compose run doc-monitor python monitor.py`

### stop
`docker compose down --rmi all --volumes --remove-orphans`

, and delete your db_data directory.

## Command line tool

`scanner/command.py` is a CLI application entrypoint.

`scanner/command.py` is also dispatched by `scanner/__main__.py`.
Please call `scanner` directory with Python command.

```sh
# Directly call command.py
python scanner/command.py --help

# [Recommended] Call scanner directory.
python scanner --help
```

See, `python scanner --help`.
This is a sample to try `scanner` with SQLite database.

```sh
#    git clone https://github.com/mahiroaug/ssl_scanner
#    cd ssl_scanner

# Choose database. MySQL and PostgreSQL are also available.
export DATABASE=sqlite:///db.sqlite

# Initialize 'Certificates' table. ('./db.sqlite' file will be created.)
python scanner init

# Register domains to scan certificates.
python scanner add google.com
python scanner add github.com

# Show registered domains in the database.
python scanner list

#    1: google.com   valid_until=None check_at=None
#    2: github.com   valid_until=None check_at=None

# Check the TLS certificate via HTTPS,
# and store a results to the database
python scanner scan google.com

#   Subject:   *.google.com
#   notBefore: 2023-02-08 04:34:30  ( 20230208043430Z )
#   notAfter:  2023-05-03 04:34:29  ( 20230503043429Z )
#   Issuer:    GTS CA 1C3
#   Algorithm: sha256WithRSAEncryption
#   Checkdate: 2023-03-04 06:06:10
#   1: google.com   until=2023-05-03 (60 days), check_at=2023-03-04 06:06:10)

python scanner list
#   2: github.com   valid_until=None check_at=None
#   1: google.com   until=2023-05-03 (60 days), check_at=2023-03-04 06:06:10)

python scanner list -o json
# [{"ID": 2, "Domain": "github.com", "Subject": null, "Issuer": null, "SigAlgorithm": null, "Valid_From": null, "Valid_To": null, "Last_Check": null, "Remaining_Days": null}, {"ID": 1, "Domain": "google.com", "Subject": "*.google.com", "Issuer": "GTS CA 1C3", "SigAlgorithm": "sha256WithRSAEncryption", "Valid_From": "2023-02-08Z", "Valid_To": "2023-05-03Z", "Last_Check": "2023-03-04T06:06:10Z", "Remaining_Days": 60}]

python scanner delete github.com
```

Support to scan multiple domains in the database with `bulkscan`.

```sh
# Scan all domains with 3 worker processes.
export DATABASE=sqlite:///db.sqlite
python scanner bulkscan --allocate 1/3 &
python scanner bulkscan --allocate 2/3 &
python scanner bulkscan --allocate 3/3 &
```

`bulkscan` command requires `--allocate` option.
See, `python scanner bulkscan --help`.


Support to load domains from domain list files to the database.

```sh
# Read `domainlist.txt` file and insert new records to the database.
export DATABASE=sqlite:///db.sqlite
python scanner load domainlist.txt

# If you want to delete records, that's are not listed in `domainlist.txt` file,
# please pass `-d` or `--delete` option.
# This command will check the text file, and insert newly listed domains, delete not listed domains.
python scanner load --delete domainlist.txt
```
