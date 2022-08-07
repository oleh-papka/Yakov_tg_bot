import logging

from utils import load_env_variable


class Config:
    BOT_VERSION = 'v0.0.1'

    DEBUG_FLAG = bool(load_env_variable('DEBUG_FLAG', int))  # If enabled shows all logging info
    WEBHOOK_FLAG = bool(load_env_variable('WEBHOOK_FLAG', int))  # For Heroku usage set to True else False

    BOT_TOKEN = load_env_variable('BOT_TOKEN')  # Your bot token

    # If hosting on Heroku
    BOT_LINK = load_env_variable('BOT_LINK', raise_if_none=WEBHOOK_FLAG)
    # Heroku dynamically allocates application port and sets it to PORT env var,
    # but to stick with naming in code I use BOT_PORT
    BOT_PORT = load_env_variable('PORT', int, raise_if_none=WEBHOOK_FLAG)

    CREATOR_ID = 514328460  # Please don't remove leave credit to author
    OWNER_ID = load_env_variable('OWNER_ID', int)  # Change according to your Telegram id

    CMC_API_TOKEN = load_env_variable('CMC_API_TOKEN')  # CoinMarketCup API
    SCREENSHOT_API_TOKEN = load_env_variable('SCREENSHOT_API_TOKEN')  # Screenshot api
    OWM_API_TOKEN = load_env_variable('OWM_API_TOKEN')  # OpenWeatherMap API

    DB_HOST = load_env_variable('DB_HOST')
    DB_NAME = load_env_variable('DB_NAME')
    DB_PASS = load_env_variable('DB_PASS')
    DB_PORT = load_env_variable('DB_PORT')
    DB_USER = load_env_variable('DB_USER')
    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SPACING = '⠀⠀  '

    BOT_COMMANDS = [
        ('weather', 'Погода у Тернополі'),
        ('crypto', 'Трішки про крипту'),
        ('currency', 'Дані по валюті'),
        ('ruloss', 'Втрати кацапні'),
        ('tip_developer', 'Тестові донейти'),
        ('help', 'Підказка')
    ]

    CRYPTO_COIN_IDS = [1, 1027, 1839, 5426]

    logging_lvl = logging.DEBUG if DEBUG_FLAG else logging.INFO

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging_lvl)

    LOGGER = logging.getLogger(__name__)
