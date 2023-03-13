import logging

from telegram.ext import (Application,
                          MessageHandler,
                          filters)

from src.commands import (help_command_handler,
                          start_command_handler,
                          settings_conversation_handler,
                          ru_losses_handler,
                          crypto_command_handler,
                          currency_command_handler,
                          profile_conversation_handler,
                          feedback_handler,
                          feedback_reply_handler,
                          weather_command_handler,
                          precheckout_handler,
                          successful_payment_handler,
                          tip_developer_handler)
from src.config import Config
from src.handlers import (error_handler,
                          unknown_messages,
                          days_passed_handler)
from src.utils.db_utils import check_db

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Check if DB exists DB
    if not check_db():
        logger.critical("DB not found!")
        exit()

    # Register commands
    application.add_handler(start_command_handler)
    application.add_handler(help_command_handler)
    application.add_handler(settings_conversation_handler)
    application.add_handler(profile_conversation_handler)
    application.add_handler(weather_command_handler)
    application.add_handler(ru_losses_handler)
    application.add_handler(crypto_command_handler)
    application.add_handler(currency_command_handler)
    application.add_handler(feedback_handler)
    application.add_handler(feedback_reply_handler)

    # Register other handlers
    application.add_handler(days_passed_handler)

    # Test tip handlers
    application.add_handler(tip_developer_handler)
    application.add_handler(precheckout_handler)
    application.add_handler(successful_payment_handler)

    # Register error handlers
    application.add_error_handler(error_handler)
    application.add_handler(MessageHandler(filters.ALL, unknown_messages))

    if Config.WEBHOOK_FLAG:
        application.run_webhook(
            listen="0.0.0.0",
            port=Config.BOT_PORT,
            webhook_url=Config.BOT_LINK
        )
    else:
        application.run_polling()


if __name__ == '__main__':
    main()
