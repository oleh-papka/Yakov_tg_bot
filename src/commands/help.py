from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from src.config import Config
from src.utils import escape_md2_no_links
from src.utils.message_utils import send_typing_action


def _compose_help_message() -> str:
    help_message_text = ("Я Yakov, персональний асистент, а ось команди, які я знаю:\n\n"
                         "/start - Привітулька від бота\n")

    for command, description in Config.BOT_COMMANDS:
        help_message_text += f"/{command} - {description}\n"

    help_message_text += (f"\nБот створений [цим](tg://user?id={Config.CREATOR_ID}) розробником,\n"
                          f"за допомогою [python-telegram-bot](https://python-telegram-bot.org/).\n"
                          f"Код проекту на GitHub [Yakov_tg_bot](https://github.com/OlegPapka2/Yakov_tg_bot)\n\n"
                          f"Поточна версія бота: {Config.BOT_VERSION}")

    return help_message_text


@send_typing_action
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message

    await message.reply_text(escape_md2_no_links(_compose_help_message()),
                             parse_mode=ParseMode.MARKDOWN_V2,
                             disable_web_page_preview=True)


help_command_handler = CommandHandler('help', help_command)
