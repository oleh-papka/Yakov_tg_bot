from telegram import ParseMode, ChatAction, Update
from telegram.ext import CommandHandler, CallbackContext

from config import Config
from utils.message_utils import clear_str_md2


def _compose_help_message() -> str:
    msg = "Я Yakov, персональний асистент, а ось команди, які я знаю:\n\n"

    for command, description in Config.BOT_COMMANDS:
        msg += f'/{command} - {description}\n'

    msg += f"\nБот створений [цим](tg://user?id={Config.CREATOR_ID}) розробником,\n" \
           f"за допомогою [python-telegram-bot](https://python-telegram-bot.org/).\n" \
           f"Код проекту на GitHub [Yakov_tg_bot](https://github.com/OlegPapka2/Yakov_tg_bot)\n\n" \
           f"Поточна версія бота: {Config.BOT_VERSION}"

    return msg


def help_command(update: Update, context: CallbackContext) -> None:
    message = update.message

    message.reply_chat_action(ChatAction.TYPING)
    message.reply_text(
        clear_str_md2(_compose_help_message(), exclude=['[', ']', '(', ')']),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True)


help_command_handler = CommandHandler('help', help_command)
