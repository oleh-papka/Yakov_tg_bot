from telegram import ChatAction, Update
from telegram.ext import MessageHandler, Filters, CallbackContext

from crud.user import manage_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action


@create_session
@send_chat_action(ChatAction.TYPING)
def unknown_messages(update: Update, context: CallbackContext, db):
    update = update.message
    user = update.from_user
    manage_user(db, user)

    msg = 'Перепрошую, але я не знаю що робити😅\n\nПідказка - /help'
    update.reply_text(msg, quote=True)


unknown_handler = MessageHandler(Filters.all, unknown_messages)
