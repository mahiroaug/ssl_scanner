# ssl_scanner
Analyzing SSL certificates for a website.

# How To Use

## Create envifonment file
 - `mysql/env_mysql.env`
 - `monitor/env_monitor.env`
 - `scanner/env_scanner.env`

## Make CSV file (a list of FQDNs to be surveyed)
 - `mysql/FQDN.csv`


## build & run
### config check
`docker compose config`

### build
`docker compose build`

### run
`docker compose up -d`

###  (in case of modified)
`docker compose up --build -d`

### post message in slack
`docker compose run doc-monitor python monitor.py`

### stop
`docker compose down --rmi all --volumes --remove-orphans`

