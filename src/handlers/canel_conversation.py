import logging

from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton, Message)
from telegram.ext import ConversationHandler, ContextTypes

cancel_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]])
logger = logging.getLogger(__name__)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    conversation_canceled_message_text = '🚫 Попередній діалог завершено.'

    if update.callback_query:
        query = update.callback_query
        message = query.message
        await query.answer()
        await message.edit_reply_markup(reply_markup=None)
    else:
        markup_msg = context.user_data.get('markup_msg')
        await markup_msg.edit_reply_markup(reply_markup=None)

    command_msg = context.user_data.get('command_msg')
    await command_msg.reply_text(conversation_canceled_message_text, quote=True)
    context.user_data.clear()

    return ConversationHandler.END
