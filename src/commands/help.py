from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from config import Config
from utils import escape_md2_no_links
from utils.message_utils import send_typing_action


@send_typing_action
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user

    help_message_text = ("Я Yakov, персональний асистент, а ось команди, які я знаю:\n\n"
                         "/start - Привітулька від бота\n")

    for command, description, for_admin in Config.BOT_COMMANDS:
        if for_admin and user.id != Config.OWNER_ID:
            continue

        help_message_text += f"/{command} - {description}\n"

    help_message_text += (f"\nБот створений [цим](tg://user?id={Config.CREATOR_ID}) розробником,\n"
                          f"за допомогою [python-telegram-bot](https://python-telegram-bot.org/).\n"
                          f"Код проекту на GitHub [Yakov_tg_bot](https://github.com/OlegPapka2/Yakov_tg_bot)\n\n"
                          f"Поточна версія бота: {Config.BOT_VERSION}")

    await message.reply_text(escape_md2_no_links(help_message_text),
                             parse_mode=ParseMode.MARKDOWN_V2,
                             disable_web_page_preview=True)


help_command_handler = CommandHandler('help', help_command)
