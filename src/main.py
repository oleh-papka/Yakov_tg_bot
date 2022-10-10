import logging

from telegram.ext import Updater

from commands import (
    start_command_handler,
    help_command_handler,
    crypto_command_handler,
    currency_command_handler,
    ru_losses_handler,
    tip_developer_handler,
    precheckout_handler,
    successful_payment_handler,
    weather_command_handler,
    profile_conversation_handler,
    feedback_handler,
    feedback_reply_handler,
    settings_conversation_handler
)
from config import Config
from handlers import (
    error_handler,
    unknown_handler,
    days_passed_handler
)

logger = logging.getLogger(__name__)


def main() -> None:
    updater = Updater(Config.BOT_TOKEN, use_context=True)
    bot = updater.bot
    disp = updater.dispatcher

    disp.add_handler(start_command_handler)
    disp.add_handler(help_command_handler)
    disp.add_handler(crypto_command_handler)
    disp.add_handler(currency_command_handler)
    disp.add_handler(ru_losses_handler)
    disp.add_handler(weather_command_handler)
    disp.add_handler(tip_developer_handler)
    disp.add_handler(precheckout_handler)
    disp.add_handler(successful_payment_handler)
    disp.add_handler(settings_conversation_handler)
    disp.add_handler(profile_conversation_handler)
    disp.add_handler(feedback_handler)
    disp.add_handler(feedback_reply_handler)

    # Text regex handlers
    disp.add_handler(days_passed_handler)
    disp.add_handler(unknown_handler)

    disp.add_error_handler(error_handler)   # Error handler

    bot.set_my_commands(Config.BOT_COMMANDS)

    if Config.WEBHOOK_FLAG:
        logger.info(f'Starting bot at {Config.BOT_LINK}')
        updater.start_webhook(listen='0.0.0.0',
                              port=Config.BOT_PORT,
                              url_path=Config.BOT_TOKEN,
                              webhook_url=Config.BOT_LINK + Config.BOT_TOKEN)
    else:
        logger.info('Starting bot locally')
        updater.start_polling()

    logger.info(f'Bot ({bot.get_me().name}) successfully started!')
    updater.idle()


if __name__ == '__main__':
    main()
