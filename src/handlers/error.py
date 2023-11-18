import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config import Config
from utils.message_utils import escape_md2

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err_msg_len = 1000 - 4  # Because "...\n" used

    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    if len(tb_string) > err_msg_len:
        tb_string = "...\n" + tb_string[-err_msg_len:].strip()

    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    # Inform developer
    msg = (
        f"⚠ Ситуація\n\n"
        f"```json\n"
        f"update = {escape_md2(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        f"```"
    )
    msg2 = (
        f"```python\n"
        f"context.chat_data = {escape_md2(str(context.chat_data))}"
        f"```"
        f"\n```python\n"
        f"context.user_data = {escape_md2(str(context.user_data))}"
        f"```"
    )
    msg3 = (
        f"```python\n"
        f"{escape_md2(tb_string)}"
        f"```"
    )

    await context.bot.send_message(chat_id=Config.OWNER_ID, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
    await context.bot.send_message(chat_id=Config.OWNER_ID, text=msg2, parse_mode=ParseMode.MARKDOWN_V2)
    await context.bot.send_message(chat_id=Config.OWNER_ID, text=msg3, parse_mode=ParseMode.MARKDOWN_V2)

    # Inform user
    error_text = 'Перепрошую, щось пішло не так. Я уже повідомив розробника.\n\nПідказка - /help'

    if update:
        await update.effective_message.reply_text(text=error_text, reply_to_message_id=update.effective_message)
