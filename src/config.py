import logging
import sys
from warnings import filterwarnings

from loguru import logger
from telegram.warnings import PTBUserWarning

from utils.env_utils import load_env_variable


class Config:
    ###########################################################################
    #                         Set up env vars below ⬇                         #
    ###########################################################################
    DEBUG_FLAG = bool(load_env_variable('DEBUG_FLAG', int))  # Enables debug level logging

    BOT_TOKEN = load_env_variable('BOT_TOKEN')  # Your Telegram bot token

    OWNER_ID = load_env_variable('OWNER_ID', int)  # Bot owner Telegram id
    TESTER_ID = load_env_variable('TESTER_ID', int, False)  # Bot tester Telegram id

    CMC_API_TOKEN = load_env_variable('CMC_API_TOKEN')  # CoinMarketCup API token
    SCREENSHOT_API_TOKEN = load_env_variable('SCREENSHOT_API_TOKEN')  # Screenshot api token
    OWM_API_TOKEN = load_env_variable('OWM_API_TOKEN')  # OpenWeatherMap API token

    DB_URL = load_env_variable('DB_URL')  # URL to your db

    ###########################################################################
    #               Heroku hosting only. Currently unsupported!               #
    ###########################################################################
    WEBHOOK_FLAG = bool(load_env_variable('WEBHOOK_FLAG', int))  # Enables webhooks
    BOT_LINK = load_env_variable('BOT_LINK', error_if_none=WEBHOOK_FLAG)
    # Heroku dynamically allocates application port and sets it to `PORT` env var
    BOT_PORT = load_env_variable('PORT', int, error_if_none=WEBHOOK_FLAG)

    ###########################################################################
    #                        Do not change line below ⬇                       #
    ###########################################################################
    CREATOR_ID = 514328460  # Please credit the author (olegpapka2@gmail.com)

    SPACING = '⠀⠀  '  # Main whitespace characters used in formatting

    BOT_VERSION = 'v0.1.0'

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

    class InterceptLogsHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists.
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message.
            frame, depth = sys._getframe(6), 6
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    format = ('<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name: '
              '<20.20}</cyan> | <level>{message}</level> ')

    logger.remove()
    logger.add(sys.stderr, format=format)
    logger.level("DEBUG", color="<fg #787878>")
    logger.level("INFO", color="<fg #ffffff>")

    logging.basicConfig(handlers=[InterceptLogsHandler()], level=logging_lvl, force=True)

    if not DEBUG_FLAG:
        filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
