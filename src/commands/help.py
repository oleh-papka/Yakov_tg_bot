from telegram import ParseMode, ChatAction, Update, MessageEntity
from telegram.ext import CommandHandler, CallbackContext

from config import Config
from crud.user import auto_create_user
from utils.db_utils import create_session
from utils.message_utils import escape_str_md2, send_chat_action


def _compose_help_message() -> str:
    msg = "Я Yakov, персональний асистент, а ось команди, які я знаю:\n\n"

    msg += f'/start - Привітулька від бота\n'
    for command, description in Config.BOT_COMMANDS:
        msg += f'/{command} - {description}\n'

    msg += f"\nБот створений [цим](tg://user?id={Config.CREATOR_ID}) розробником,\n" \
           f"за допомогою [python-telegram-bot](https://python-telegram-bot.org/).\n" \
           f"Код проекту на GitHub [Yakov_tg_bot](https://github.com/OlegPapka2/Yakov_tg_bot)\n\n" \
           f"Поточна версія бота: {Config.BOT_VERSION}"

    return msg


@create_session
@send_chat_action(ChatAction.TYPING)
def help_command(update: Update, context: CallbackContext, db) -> None:
    message = update.message
    user = message.from_user
    auto_create_user(db, user)

    message.reply_text(
        escape_str_md2(_compose_help_message(), exclude=MessageEntity.TEXT_LINK),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True)


help_command_handler = CommandHandler('help', help_command)
