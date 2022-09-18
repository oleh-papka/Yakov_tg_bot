# Yakov_tg_bot

This is simple Telegram helper bot, made for simplifying some daily routines.

New features will be added soon...


## Setup bot

### Requirements:

- PostgreSQL database (hypothetically you could use any other, but I'm not 100% shure)
- Python 3.10 (haven't checked lower versions, but why to use them?)
- And external libraries could be found in [`requirements.txt`](./requirements.txt)


### Bot config

Environmental variables example template could be found in [`.env.example`](./.env.example)
file.
Set `WEBHOOK_FLAG` to `1` for running on Heroku and to `0` for running locally.


### Initial database populating

Bot currently uses some predefined data. So you need to populate your database before 
running bot. Just run [`setup.py`](./src/setup.py) from project root.

```bash
$ python3 ./src/setup.py
# or for Windows  
$ py ./src/setup.py
```


## Development

Read the [`CONTRIBUTING.md`](./CONTRIBUTING.md) file.