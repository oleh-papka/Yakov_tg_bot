from telegram import Update, ChatAction
from telegram.ext import ConversationHandler, CallbackContext

from config import Config
from utils.message_utils import send_chat_action


@send_chat_action(ChatAction.TYPING)
def cancel(update: Update, context: CallbackContext):
    CONVERSATION_CANCELED = '🚫 Ви завершили попередній діалог'

    if update.callback_query:
        query = update.callback_query
        message = query.message
        user_id = message.chat.id

        query.answer()
        query.edit_message_reply_markup(reply_markup=None)

        Config.LOGGER.debug(f"User '{user_id}' canceled the conversation")
        message.reply_text(CONVERSATION_CANCELED, quote=True)
    else:
        message = update.message
        user_id = message.from_user.id
        reply_msg_id = context.user_data['reply_msg_id']

        Config.LOGGER.debug(f"User '{user_id}' canceled the conversation")
        message.reply_text(CONVERSATION_CANCELED, reply_to_message_id=reply_msg_id)

    context.user_data.clear()
    return ConversationHandler.END
