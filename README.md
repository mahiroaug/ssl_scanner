# ssl_scanner
Analyzing SSL certificates for a website.

# How To
1. `.env`ファイルを作成

```
MYSQL_ROOT_PASSWORD=<your_mysql_password>
```

2. run

config check

`docker compose config`

run

`docker compose up --build -d`

stop

`dockercompose down --rmi all --volumes --remove-orphans`
