import logging

from utils import load_env_variable


class Config:
    BOT_VERSION = 'v0.0.1'

    DEBUG_FLAG = bool(load_env_variable('DEBUG_FLAG', int))  # If enabled shows all logging info
    WEBHOOK_FLAG = bool(load_env_variable('WEBHOOK_FLAG', int))  # For Heroku usage set to True else False

    BOT_TOKEN = load_env_variable('BOT_TOKEN')  # Your bot token

    # If hosting on Heroku
    BOT_LINK = load_env_variable('BOT_LINK', raise_if_none=WEBHOOK_FLAG)
    BOT_PORT = load_env_variable('BOT_PORT', int, raise_if_none=WEBHOOK_FLAG)

    CREATOR_ID = 514328460  # Please don't remove leave credit to author
    OWNER_ID = load_env_variable('OWNER_ID', int)  # Change according to your Telegram id

    CMC_API_TOKEN = load_env_variable('CMC_API_TOKEN')  # CoinMarketCup API
    SCREENSHOT_API_TOKEN = load_env_variable('SCREENSHOT_API_TOKEN')  # Screenshot api
    OWM_API_TOKEN = load_env_variable('OWM_API_TOKEN')  # OpenWeatherMap API

    SPACING = '⠀⠀  '

    BOT_COMMANDS = [
        ('crypto', 'Трішки про крипту'),
        ('currency', 'Дані по валюті'),
        ('ruloss', 'Втрати кацапні'),
        ('help', 'Підказка'),
        ('tip_developer', 'Тестові донейти'),
    ]

    CRYPTO_COIN_IDS = [1, 1027, 1839, 5426]

    logging_lvl = logging.DEBUG if DEBUG_FLAG else logging.INFO

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging_lvl)

    LOGGER = logging.getLogger(__name__)
