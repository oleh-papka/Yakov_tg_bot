# Yakov_tg_bot

[![DeepSource](https://deepsource.io/gh/Oleh-Papka/Yakov_tg_bot.svg/?label=active+issues&show_trend=true&token=OIiAWpkSJ_AG7k9ijIN_n4Os)](https://deepsource.io/gh/Oleh-Papka/Yakov_tg_bot/?ref=repository-badge)
[![DeepSource](https://deepsource.io/gh/Oleh-Papka/Yakov_tg_bot.svg/?label=resolved+issues&show_trend=true&token=OIiAWpkSJ_AG7k9ijIN_n4Os)](https://deepsource.io/gh/Oleh-Papka/Yakov_tg_bot/?ref=repository-badge)


[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Oleh-Papka_Yakov_tg_bot&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Oleh-Papka_Yakov_tg_bot)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Oleh-Papka_Yakov_tg_bot&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Oleh-Papka_Yakov_tg_bot)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=Oleh-Papka_Yakov_tg_bot&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=Oleh-Papka_Yakov_tg_bot)


![GitHub issues](https://img.shields.io/github/issues/Oleh-Papka/Yakov_tg_bot?logo=GitHub)
![GitHub](https://img.shields.io/github/license/Oleh-Papka/Yakov_tg_bot?logo=GitHub)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Oleh-Papka/Yakov_tg_bot?logo=GitHub)


This is a simple Telegram helper bot designed to simplify daily routines.
Initially, it was a personal project that grew into one of my largest pet projects,
which I enjoy maintaining and supporting.

P.S. New features will be added soon...

P.P.S. You can try it [here](https://t.me/Yakov_the_bot).

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
