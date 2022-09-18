import logging
import os

from utils.env_utils import load_env_variable


class Config:
    ###########################################################################
    #                         Set up env vars below ⬇                         #
    ###########################################################################
    DEBUG_FLAG = bool(load_env_variable('DEBUG_FLAG', int))  # Enables debug

    BOT_TOKEN = load_env_variable('BOT_TOKEN')  # Your Telegram bot token

    OWNER_ID = load_env_variable('OWNER_ID', int)  # Bot owner Telegram id
    TESTER_ID = load_env_variable('TESTER_ID', int)  # Bot tester Telegram id

    CMC_API_TOKEN = load_env_variable('CMC_API_TOKEN')  # CoinMarketCup API token
    SCREENSHOT_API_TOKEN = load_env_variable('SCREENSHOT_API_TOKEN')  # Screenshot api token
    OWM_API_TOKEN = load_env_variable('OWM_API_TOKEN')  # OpenWeatherMap API token

    DB_URL = load_env_variable('DB_URL')  # URL to your db

    ###########################################################################
    #                           Heroku hosting only!                          #
    ###########################################################################
    WEBHOOK_FLAG = bool(load_env_variable('WEBHOOK_FLAG', int))  # Enables webhooks
    BOT_LINK = load_env_variable('BOT_LINK', raise_if_none=WEBHOOK_FLAG)
    # Heroku dynamically allocates application port and sets it to `PORT` env var
    BOT_PORT = load_env_variable('PORT', int, raise_if_none=WEBHOOK_FLAG)

    ###########################################################################
    #                        Do not change line below ⬇                       #
    ###########################################################################
    CREATOR_ID = 514328460  # Please leave credit to author

    SPACING = '⠀⠀  '  # Main whitespace characters used in formatting

    BOT_VERSION = 'v0.0.3'

    BOT_COMMANDS = [
        ('weather', 'Погода'),
        ('crypto', 'Трішки про крипту'),
        ('currency', 'Дані по валюті'),
        ('ruloss', 'Втрати кацапні'),
        ('tip_developer', 'Тестові донейти'),
        ('profile', 'Профіль користувача'),
        ('feedback', 'Надіслати відгук'),
        ('settings', 'Налаштування'),
        ('help', 'Підказка')
    ]

    logging_lvl = logging.DEBUG if DEBUG_FLAG else logging.INFO
    logging.basicConfig(
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        level=logging_lvl,
        handlers=[
            logging.FileHandler(os.path.join(os.getcwd(), 'logs.log'),
                                encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
