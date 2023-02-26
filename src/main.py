import logging


from telegram.ext import Application

from src.config import Config

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(Config.BOT_TOKEN).build()
    application.run_polling()


if __name__ == '__main__':
    main()
