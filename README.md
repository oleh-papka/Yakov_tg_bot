# Yakov_tg_bot

This Telegram helper bot is designed to simplify daily routines, it implements basic functionality of Telegram Bot API.

### Features:
- Weather forecast for users city
- Crypto and fiat currency markets changes
- Casualties in russian war (russia is the terrorist state)
- Simple date calculator

## Setup bot

### Requirements:

- PostgreSQL
- Python 3.10+
- And external libraries could be found in [`requirements.txt`](./requirements.txt)

### Bot config

Environmental variables example template could be found in [`.env.example`](./.env.example) file.  
Set `WEBHOOK_FLAG` to `1` for running on Heroku (also need to specify `BOT_LINK` and `PORT` if so) and `0` for running
locally.

### Initial database populating

Bot currently uses some predefined data. So you need to populate your database before
running bot. Just run [`setup.py`](./src/setup.py) from project root. Or do nothing if docker used.

```bash
$ python3 ./src/setup.py
# or for Windows  
$ py ./src/setup.py
```

OR

```bash
$ docker-compose up   # If you want to use via Docker 
```

## Development

Before starting your contribution read the [`CONTRIBUTING.md`](./CONTRIBUTING.md) file.
