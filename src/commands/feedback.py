import re

from telegram import ChatAction, ParseMode, Update, MessageEntity
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler, MessageHandler, Filters

import models
from config import Config
from crud.feedback import get_feedback_by_msg_id, mark_read
from handlers import cancel
from utils.db_utils import create_session
from utils.message_utils import send_chat_action, escape_str_md2

CONV_START, REPLY_START, DELETE_REPLIED = 1, 2, 3


@send_chat_action(ChatAction.TYPING)
def feedback(update: Update, context: CallbackContext):
    message = update.message

    message.reply_chat_action(ChatAction.TYPING)
    msg = message.reply_text('Ок, надішліть свій фідбек:\n\nВідмінити ввід - /cancel')
    context.user_data['reply_msg_id'] = msg.message_id
    context.user_data['reply_markup'] = msg

    return CONV_START


@create_session
@send_chat_action(ChatAction.TYPING)
def feedback_get_user_text(update: Update, context: CallbackContext, db):
    message = update.message
    user_id = message.chat.id
    user = message.from_user
    text = message.text
    msg_id = message.message_id

    msg = f"Хей тобі повідомлення від [{escape_str_md2(user.first_name)}](tg://user?id={user_id})"
    if user.last_name:
        msg += f" {escape_str_md2(user.last_name)}"
    if user.username:
        msg += f" \\(@{escape_str_md2(user.username)}\\)"

    msg += f"\n\n```{escape_str_md2(text)}```\n\n"
    msg += f"Відповісти на фідбек? \\(/reply\\_feedback\\_{msg_id}\\)"

    context.bot.send_message(Config.OWNER_ID, text=msg, parse_mode=ParseMode.MARKDOWN_V2)

    msg = f'✅ Шик, уже надіслав [розробнику](tg://user?id={Config.OWNER_ID})!'
    message.reply_text(escape_str_md2(msg, exclude=MessageEntity.TEXT_LINK), parse_mode=ParseMode.MARKDOWN_V2)

    feedback_model = models.Feedback(user_id=user_id, msg_id=msg_id, msg_text=text, read_flag=False)
    db.add(feedback_model)
    db.commit()

    return ConversationHandler.END


@create_session
@send_chat_action(ChatAction.TYPING)
def feedback_reply(update: Update, context: CallbackContext, db):
    message = update.message
    msg_id = int(message.text.replace('/reply_feedback_', ''))

    feedback_model = get_feedback_by_msg_id(db, msg_id)
    if not feedback_model:
        message.reply_text(escape_str_md2(f'Дивно немає фідбеку із msg_id=`{msg_id}`', ['`']),
                           parse_mode=ParseMode.MARKDOWN_V2)
        return ConversationHandler.END

    context.user_data['reply_msg_id'] = {'msg_id': msg_id, 'user_id': feedback_model.user_id}

    message.reply_chat_action(ChatAction.TYPING)
    name = escape_str_md2(feedback_model.user.first_name)

    msg = f'Пишемо відповідь на фідбек користувача ' \
          f'[{name}](tg://user?id={feedback_model.user.id}):' \
          f'\n\n```{feedback_model.msg_text}```\n\n' \
          f'Відмінити ввід - /cancel'

    message.reply_text(escape_str_md2(msg, MessageEntity.TEXT_LINK, ['`']), parse_mode=ParseMode.MARKDOWN_V2)

    return REPLY_START


@create_session
@send_chat_action(ChatAction.TYPING)
def feedback_reply_text(update: Update, context: CallbackContext, db):
    message = update.message
    text = message.text

    reply_msg_id = context.user_data['reply_msg_id']['msg_id']
    reply_user_id = context.user_data['reply_msg_id']['user_id']

    msg = f"У відповідь на ваше повідомлення розробник пише:\n\n"
    msg += f"{escape_str_md2(text)}\n\n"
    msg += f"Ще раз дякую за фідбек 🙃"

    context.bot.send_message(reply_user_id, text=msg, parse_mode=ParseMode.MARKDOWN_V2,
                             reply_to_message_id=reply_msg_id)

    mark_read(db, reply_msg_id)

    message.reply_chat_action(ChatAction.TYPING)
    message.reply_text('✅ Чудово, я уже відповів користувачу!')

    return ConversationHandler.END


feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('feedback', feedback)],
    states={
        CONV_START: [
            MessageHandler(Filters.regex(re.compile(r'^/cancel$')), cancel),
            MessageHandler(Filters.text, feedback_get_user_text)
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel)
    ],
    conversation_timeout=300.0
)

feedback_reply_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(re.compile(r'/reply_feedback_\d+')), feedback_reply)],
    states={
        REPLY_START: [
            MessageHandler(Filters.regex(re.compile(r'^/cancel$')), cancel),
            MessageHandler(Filters.text, feedback_reply_text)
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel)
    ],
    conversation_timeout=300.0
)
