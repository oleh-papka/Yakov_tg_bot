from telegram import Update, ParseMode, MessageEntity, ChatAction
from telegram.ext import CommandHandler, CallbackContext

from config import Config
from crud.user import auto_create_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action, escape_str_md2


@create_session
@send_chat_action(ChatAction.TYPING)
def start(update: Update, context: CallbackContext, db) -> None:
    message = update.message
    user = message.from_user
    auto_create_user(db, user)

    msg = f"Привіт {user.first_name}, я Yakov і створений тому, що " \
          f"моєму [розробнику](tg://user?id={Config.CREATOR_ID}) було нудно.\n" \
          f"Я постійно отримую апдейти та нові функції, залишайся зі мною, " \
          f"розробнику приємно, а тобі цікаві фішки 🙃\n\n" \
          f"Підказка - /help\n\n" \
          f"P.S. Підтримати ЗСУ можна [тут](https://savelife.in.ua/donate/#payOnce), Слава Україні!"

    msg = escape_str_md2(msg, MessageEntity.TEXT_LINK)
    message.reply_text(msg,
                       parse_mode=ParseMode.MARKDOWN_V2,
                       disable_web_page_preview=True)


start_command_handler = CommandHandler('start', start)
