# ssl_scanner
Analyzing SSL certificates for a website.

# How To
1. Create `.env`

```
MYSQL_ROOT_PASSWORD=<your_mysql_password>
SLACK_BOT_TOKEN=<your_slack_bot_token>
SLACK_CHANNEL_ID=<your_slack>
```

2. run

### config check
`docker compose config`

### build
`docker compose build`

### run
`docker compose up -d`

#### (in case of modified)
`docker compose up --build -d`

#### post message in slack
`docker compose run doc-monitor python monitor.py`

### stop
`docker compose down --rmi all --volumes --remove-orphans`

