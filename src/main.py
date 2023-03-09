import logging

from telegram.ext import Application, MessageHandler, filters

from src.commands import (help_command_handler,
                          start_command_handler,
                          settings_conversation_handler,
                          ru_losses_handler,
                          crypto_command_handler,
                          currency_command_handler,
                          profile_conversation_handler)
from src.config import Config
from src.handlers import error_handler, unknown_messages

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Register commands
    application.add_handler(settings_conversation_handler)
    application.add_handler(profile_conversation_handler)
    application.add_handler(start_command_handler)
    application.add_handler(help_command_handler)
    application.add_handler(ru_losses_handler)
    application.add_handler(crypto_command_handler)
    application.add_handler(currency_command_handler)

    # Register error handlers
    application.add_error_handler(error_handler)
    application.add_handler(MessageHandler(filters.ALL, unknown_messages))

    application.run_polling()


if __name__ == '__main__':
    main()
