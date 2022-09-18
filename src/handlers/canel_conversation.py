import logging

from telegram import Update, ChatAction, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackContext

from utils.message_utils import send_chat_action

cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]])
logger = logging.getLogger(__name__)


@send_chat_action(ChatAction.TYPING)
def cancel(update: Update, context: CallbackContext):
    CONVERSATION_CANCELED = '🚫 Попередній діалог завершено.'

    if update.callback_query:
        query = update.callback_query
        message = query.message
        user_id = message.chat.id

        query.answer()
        message.edit_reply_markup(reply_markup=None)

        logger.debug(f"User '{user_id}' canceled the conversation")
        message.reply_text(CONVERSATION_CANCELED, quote=True)
    else:
        message = update.message
        user_id = update.effective_user.id
        reply_msg_id = context.user_data['cancel_reply_msg_id']

        if cancel_reply_markup_msg_id := context.user_data.get('cancel_reply_markup_msg_id'):
            context.bot.edit_message_reply_markup(user_id, cancel_reply_markup_msg_id)

        logger.debug(f"User '{user_id}' canceled the conversation")
        message.reply_text(CONVERSATION_CANCELED, reply_to_message_id=reply_msg_id)

    context.user_data.clear()
    return ConversationHandler.END
