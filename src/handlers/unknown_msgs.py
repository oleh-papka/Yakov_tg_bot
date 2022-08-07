from telegram import ChatAction, Update
from telegram.ext import MessageHandler, Filters, CallbackContext

from crud.user import add_user_to_db
from utils.message_utils import send_chat_action


@add_user_to_db
@send_chat_action(ChatAction.TYPING)
def unknown_messages(update: Update, context: CallbackContext):
    update = update.message
    msg = 'Перепрошую, але я не знаю що робити😅\n\nПідказка - /help'
    update.reply_text(msg, quote=True)


unknown_handler = MessageHandler(Filters.all, unknown_messages)
