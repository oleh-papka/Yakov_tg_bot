import html
import json
import traceback

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from config import Config


def error_handler(update: Update, context: CallbackContext) -> None:
    ERROR_MSG_LENGTH = 1000 - 4  # Because "...\n" used

    Config.LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    if len(tb_string) > ERROR_MSG_LENGTH:
        tb_string = "...\n" + tb_string[-ERROR_MSG_LENGTH:].strip()

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"⚠ Ситуація\n\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>"
    )
    message2 = (
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>"
    )
    message3 = f"<pre>{html.escape(tb_string)}</pre>"

    context.bot.send_message(chat_id=Config.OWNER_ID, text=message, parse_mode=ParseMode.HTML)
    context.bot.send_message(chat_id=Config.OWNER_ID, text=message2, parse_mode=ParseMode.HTML)
    context.bot.send_message(chat_id=Config.OWNER_ID, text=message3, parse_mode=ParseMode.HTML)
