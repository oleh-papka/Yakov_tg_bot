from sqlalchemy.orm import Session
from telegram import ChatAction, Update
from telegram.ext import MessageHandler, Filters, CallbackContext

from crud.user import create_or_update_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action


@create_session
@send_chat_action(ChatAction.TYPING)
def unknown_messages(update: Update, context: CallbackContext, db: Session):
    update = update.message
    user = update.from_user
    create_or_update_user(db, user)

    msg = 'Перепрошую, але я не знаю що робити😅\n\nПідказка - /help'
    update.reply_text(msg, quote=True)


unknown_handler = MessageHandler(Filters.all, unknown_messages)
