from telegram import Update
from telegram.ext import ContextTypes

from utils.message_utils import send_typing_action


@send_typing_action
async def unknown_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = 'Перепрошую, але я не знаю що робити😅\n\nПідказка - /help'

    await update.effective_message.reply_text(msg, quote=True)
