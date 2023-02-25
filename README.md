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

- `nodes` is a number of parallels.
- `node_id` is each node.

example:
- `docker compose run doc-scanner controler.py 4 1`
- `docker compose run doc-scanner controler.py 4 2`
- `docker compose run doc-scanner controler.py 4 3`
- `docker compose run doc-scanner controler.py 4 4`

or

`seq 1 4 | parallel docker compose run doc-scanner controler.py 4 {}`

### post message in slack
`docker compose run doc-monitor python monitor.py`

### stop
`docker compose down --rmi all --volumes --remove-orphans`

, and delete your db_data directory.

