import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.config import Config

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err_msg_len = 1000 - 4  # Because "...\n" used

    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    if len(tb_string) > err_msg_len:
        tb_string = "...\n" + tb_string[-err_msg_len:].strip()

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    # Inform developer
    msg = (
        f"⚠ Ситуація\n\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>"
    )
    msg2 = (
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>"
    )
    msg3 = f"<pre>{html.escape(tb_string)}</pre>"

    await context.bot.send_message(chat_id=Config.OWNER_ID, text=msg, parse_mode=ParseMode.HTML)
    await context.bot.send_message(chat_id=Config.OWNER_ID, text=msg2, parse_mode=ParseMode.HTML)
    await context.bot.send_message(chat_id=Config.OWNER_ID, text=msg3, parse_mode=ParseMode.HTML)

    # Inform user
    msg = 'Перепрошую, щось пішло не так. Я уже повідомив розробника.\n\nПідказка - /help'

    if update.callback_query:
        query = update.callback_query
        message = query.message
    else:
        message = update.message

    await message.reply_text(msg, quote=True)
