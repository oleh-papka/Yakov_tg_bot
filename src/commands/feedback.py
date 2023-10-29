import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (filters,
                          MessageHandler,
                          ConversationHandler,
                          CommandHandler,
                          ContextTypes,
                          CallbackQueryHandler)

from config import Config
from crud.feedback import (create_feedback,
                               create_feedback_reply,
                               mark_feedback_read,
                               get_feedback_by_id)
from crud.user import create_or_update_user
from handlers.canel_conversation import cancel, cancel_keyboard
from utils.db_utils import get_session
from utils.message_utils import escape_md2, escape_md2_no_links, send_typing_action

GET_MESSAGE, REPLY_START, SUBMIT_SENDING = 1, 2, 3


@send_typing_action
async def write_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    context.user_data['markup_msg'] = await message.reply_text('Ок, напиши свій фідбек нижче:',
                                                               reply_markup=cancel_keyboard)

    return GET_MESSAGE


@send_typing_action
async def feedback_get_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']

    await markup_msg.edit_reply_markup()

    async with get_session() as session:
        feedback_model = await create_feedback(session=session,
                                               user_id=user.id,
                                               msg_id=message.message_id,
                                               msg_text=message.text)

    # Firstly send to developer feedback
    to_dev_text = (f"Фідбек від {user.name}:\n\n{message.text}\n\n"
                   f"Відповісти на фідбек? ({Config.FEEDBACK_REPLY_COMMAND}{feedback_model.id})")

    await context.bot.send_message(Config.OWNER_ID, text=escape_md2(to_dev_text),
                                   parse_mode=ParseMode.MARKDOWN_V2)

    # Inform user that feedback sent
    if Config.DEBUG_FLAG or user.id != Config.OWNER_ID:
        to_user_text = f'✅ Шик, уже надіслав [розробнику](tg://user?id={Config.OWNER_ID})!'
        await message.reply_text(escape_md2_no_links(to_user_text), parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data.clear()
    return ConversationHandler.END


@send_typing_action
async def reply_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user

    if user.id != Config.OWNER_ID:
        await message.reply_text('❌ Но-но-но... В тебе немає прав для виконання такої команди!')
        return ConversationHandler.END

    context.user_data['command_msg'] = message

    feedback_id = int(message.text.replace(Config.FEEDBACK_REPLY_COMMAND, ''))

    async with get_session() as session:
        feedback_model = await get_feedback_by_id(session, feedback_id)

    if not feedback_model:
        await message.reply_markdown_v2(escape_md2(f'Дивно немає фідбеку із id=`{feedback_id}`', ['`']))
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data['feedback_model'] = feedback_model

    name = escape_md2(feedback_model.user.first_name)
    response_text = (f'Пишемо відповідь користувачу [{name}](tg://user?id={feedback_model.user.id}) '
                     f'на фідбек:\n\n{feedback_model.msg_text}')

    context.user_data['markup_msg'] = await message.reply_text(escape_md2_no_links(response_text, ['`']),
                                                               parse_mode=ParseMode.MARKDOWN_V2,
                                                               reply_markup=cancel_keyboard)
    return REPLY_START


@send_typing_action
async def feedback_reply_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message

    markup_msg = context.user_data['markup_msg']
    context.user_data['feedback_reply_text'] = message.text

    await markup_msg.edit_reply_markup()

    confirmation_keyboard = [
        [
            InlineKeyboardButton('Підтвердити ✅', callback_data='confirm'),
            InlineKeyboardButton('Редагувати 📝', callback_data='edit')
        ],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ]

    reply_keyboard = InlineKeyboardMarkup(confirmation_keyboard)

    await message.reply_text('Впевнений, надіслати дане повідомлення?',
                             reply_markup=reply_keyboard,
                             reply_to_message_id=message.message_id)

    return SUBMIT_SENDING


async def send_reply_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    feedback_model = context.user_data['feedback_model']
    feedback_reply_text = context.user_data['feedback_reply_text']

    response_text = (f"У відповідь на ваше повідомлення розробник пише:\n\n"
                     f"{feedback_reply_text}\n\n"
                     f"P.S. Ще раз дякую за фідбек 🙃")

    await query.edit_message_text('🆗 Уже надсилаю...', reply_markup=None)

    await context.bot.send_message(chat_id=feedback_model.user_id,
                                   text=escape_md2(response_text),
                                   parse_mode=ParseMode.MARKDOWN_V2,
                                   reply_to_message_id=feedback_model.msg_id)

    async with get_session() as session:
        await create_feedback_reply(session, feedback_model.id, feedback_model.msg_id, feedback_reply_text)
        await mark_feedback_read(session, feedback_model.id)

    await query.edit_message_text('✅ Чудово, я уже відповів користувачу!', reply_markup=None)

    context.user_data.clear()

    return ConversationHandler.END


async def edit_reply_feedback_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    edit_text = '🆗 Надішли у наступному повідомленні відповідно змінене.'
    context.user_data['markup_msg'] = await query.edit_message_text(edit_text, reply_markup=cancel_keyboard)

    return REPLY_START


feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('feedback', write_feedback)],
    states={
        GET_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(filters.TEXT, feedback_get_user_text)
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)

feedback_reply_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(re.compile(f'{Config.FEEDBACK_REPLY_COMMAND}\\d+')), reply_feedback)],
    states={
        REPLY_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(filters.TEXT, feedback_reply_check)
        ],
        SUBMIT_SENDING: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(send_reply_feedback, pattern='^confirm$'),
            CallbackQueryHandler(edit_reply_feedback_text, pattern='^edit$')
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)
