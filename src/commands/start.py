from telegram import ChatAction, Update
from telegram.ext import CommandHandler, CallbackContext

from config import Config
from utils import clear_str_md2


def start(update: Update, context: CallbackContext) -> None:
    message = update.message
    user = message.from_user

    Config.LOGGER.debug(f"New user '{user.first_name}' with user id: {user.id}")

    msg = f"Привіт {user.first_name}, я Yakov, бот створений тому, що " \
          f"моєму [розробнику](tg://user?id={Config.CREATOR_ID}) було нудно." \
          f"Я постійно отримую апдейти та нові функції, залишайся зі мною, " \
          f"розробнику приємно, а тобі цікаві фішки 🙃\n\n" \
          f"Підказка - /help\n\n" \
          f"P.S. Підтримати ЗСУ можна [тут](https://savelife.in.ua/donate/#payOnce), Слава Україні!"

    message.reply_chat_action(ChatAction.TYPING)
    message.reply_text(clear_str_md2(msg, exclude=['(', ')', '[', ']']))


start_command_handler = CommandHandler('start', start)
