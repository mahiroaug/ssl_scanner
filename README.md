# ssl_scanner
Analyzing SSL certificates for a website.

# How To Use

## Create envifonment file
 - `./.env`
  ```sh
  TZ=Tokyo/Asia
  DATABASE=sqlite:///data/db.sqlite
  SLACK_BOT_TOKEN=<YOUR_SLACK_BOT_TOKEN>
  SLACK_CHANNEL_ID=<YOUR_SLACK_CHANNEL_ID>
  ```

## Make CSV file (a list of FQDNs to be surveyed)
 - `db/domainlist.txt`
  ```sh
  example1.com
  example2.com
  example3.com
  ```


## build & run
### config check
`docker compose config`

### build
`docker compose build --no-cache`

### run (init DB)
`docker compose run --rm doc-scanner init`


### run (loading domainlist)
`ocker compose run --rm doc-scanner load data/domainlist.txt`

### run (list all)

`docker compose run --rm doc-scanner list`

### run (scan)

`docker compose run --rm doc-scanner scan <domain>`

```sh
ssl_scanner $ docker compose run --rm doc-scanner scan mineo.jp
Subject:   *.mineo.jp
notBefore: 2022-07-20 07:35:55  ( 20220720073555Z )
notAfter:  2023-08-21 07:35:54  ( 20230821073554Z )
Issuer:    AlphaSSL CA - SHA256 - G2
Algorithm: sha256WithRSAEncryption
Checkdate: 2023-03-17 02:20:45
35: mineo.jp    expire_on:2023-08-21Z (157 days), checked_at:2023-03-17T02:20:45Z
```

### run (bulkscan)

`docker compose run --rm doc-scanner bulkscan --allocate <worker_id>/<workers>`

- worker_id : a specific number of each worker
- workers   : total of workers

```sh
# 10 parallels
docker compose run --rm -d doc-scanner bulkscan --allocate 1/10
docker compose run --rm -d doc-scanner bulkscan --allocate 2/10
docker compose run --rm -d doc-scanner bulkscan --allocate 3/10
docker compose run --rm -d doc-scanner bulkscan --allocate 4/10
docker compose run --rm -d doc-scanner bulkscan --allocate 5/10
docker compose run --rm -d doc-scanner bulkscan --allocate 6/10
docker compose run --rm -d doc-scanner bulkscan --allocate 7/10
docker compose run --rm -d doc-scanner bulkscan --allocate 8/10
docker compose run --rm -d doc-scanner bulkscan --allocate 9/10
docker compose run --rm -d doc-scanner bulkscan --allocate 10/10
```

### push slack

`docker compose run --rm --entrypoint="python push_slackbot.py" doc-scanner`


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
