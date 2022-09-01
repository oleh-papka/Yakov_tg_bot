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

# Line below used for importing dependencies for initial bot setup, runs only once at first start
# from scripts.fill_db import populate_currency, populate_crypto_currency


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

    # Unknown messages handler
    disp.add_handler(unknown_handler)

    # Error handler
    disp.add_error_handler(error_handler)

    bot.set_my_commands(Config.BOT_COMMANDS)

    # Lines below should be used only once at first start of bot
    # populate_currency()
    # populate_crypto_currency()

    if Config.WEBHOOK_FLAG:
        Config.LOGGER.info(f'Starting bot at {Config.BOT_LINK}')
        updater.start_webhook(listen='0.0.0.0',
                              port=Config.BOT_PORT,
                              url_path=Config.BOT_TOKEN,
                              webhook_url=Config.BOT_LINK + Config.BOT_TOKEN)
    else:
        Config.LOGGER.info('Starting bot locally')
        updater.start_polling()

    Config.LOGGER.info('Bot successfully started!')
    updater.idle()


if __name__ == '__main__':
    main()
