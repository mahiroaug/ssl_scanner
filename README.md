# ssl_scanner
Analyzing SSL certificates for a website.

# How To
1. Create `.env`

```
MYSQL_ROOT_PASSWORD=<your_mysql_password>
SLACK_BOT_TOKEN=<your_slack_bot_token>
```

2. run

config check

`docker compose config`

run

`docker compose up --build -d`

stop

`docker compose down --rmi all --volumes --remove-orphans`
