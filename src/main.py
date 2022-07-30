from telegram.ext import Updater

from commands import (
    start_command_handler,
    help_command_handler,
    crypto_command_handler,
    weather_command_handler
)
from config import Config
from handlers import error_handler


def main() -> None:
    updater = Updater(Config.BOT_TOKEN, use_context=True)
    bot = updater.bot
    disp = updater.dispatcher

    disp.add_handler(start_command_handler)
    disp.add_handler(help_command_handler)
    disp.add_handler(crypto_command_handler)
    disp.add_handler(weather_command_handler)

    disp.add_error_handler(error_handler)

    bot.set_my_commands(Config.BOT_COMMANDS)

    if Config.WEBHOOK_FLAG:
        Config.LOGGER.debug(f'Starting bot at {Config.BOT_LINK}')
        updater.start_webhook(listen='0.0.0.0',
                              port=Config.BOT_PORT,
                              url_path=Config.BOT_TOKEN,
                              webhook_url=Config.BOT_LINK + Config.BOT_TOKEN)
    else:
        Config.LOGGER.debug('Starting bot locally')
        updater.start_polling()

    Config.LOGGER.info('Bot successfully started!')
    updater.idle()


if __name__ == '__main__':
    main()
