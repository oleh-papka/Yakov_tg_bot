import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (filters,
                          MessageHandler,
                          ConversationHandler,
                          CommandHandler,
                          ContextTypes,
                          CallbackQueryHandler)

from src.config import Config
from src.crud.feedback import (create_feedback,
                               get_feedback_by_msg_id,
                               mark_feedback_read)
from src.crud.user import create_or_update_user
from src.handlers.canel_conversation import cancel, cancel_keyboard, cancel_back_keyboard
from src.utils.db_utils import get_session
from src.utils.github_utils import create_issue
from src.utils.message_utils import escape_md2, escape_md2_no_links

FEEDBACK_START, GET_MESSAGE, REPLY_START, MAKE_ISSUE = 1, 2, 3, 4

feedback_start_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Feedback 💬', callback_data='feedback'),
     InlineKeyboardButton('Bug report 🐛', callback_data='bug_report')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
])

make_issue_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Instant Issue 📑', callback_data='instant_issue')],
    [InlineKeyboardButton('Відповісти користувачу 💬', callback_data='reply_to')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
])


async def start_feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    context.user_data['markup_msg'] = await message.reply_text('Ок, обери, що варто зробити з наведеного нижче:',
                                                               reply_markup=feedback_start_keyboard)

    return FEEDBACK_START


async def back_to_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    settings_start_text = 'Шукаєш щось інше?\nОбери з нижче наведених опцій:'

    await query.edit_message_text(text=settings_start_text, reply_markup=feedback_start_keyboard)

    return FEEDBACK_START


async def get_feedback_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    await query.answer()

    context.user_data['feedback_type'] = query.data

    if query.data == 'feedback':
        edited_text = 'Ясненько, тоді надішли мені повідомлення, яким ти хочеш поділитись із розробником нижче:'
    else:
        edited_text = ('Оу, замітив проблемки? Надішли свій bug report нижче:\n\n'
                       'P.S. Будь ласка, не забудь вказати, яка саме проблема виникла '
                       'та що зробити щоб її відтворити, дякую. '
                       'Розробник відповість, як тільки її виправить.')

    context.user_data['markup_msg'] = await message.edit_text(text=edited_text,
                                                              reply_markup=cancel_back_keyboard)

    return GET_MESSAGE


async def feedback_get_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']
    feedback_type = context.user_data['feedback_type']
    feedback_type_text = 'фідбек' if feedback_type == 'feedback' else 'bug report'

    await markup_msg.edit_reply_markup()

    async with get_session() as session:
        await create_feedback(session=session,
                              feedback_type=feedback_type,
                              user_id=user.id,
                              msg_id=message.message_id,
                              msg_text=message.text)

    # Firstly send to developer feedback
    to_dev_text = (f"Повідомлення \\({feedback_type_text}\\) від {escape_md2(user.name)}:\n\n"
                   f"{escape_md2(message.text)}\n\n"
                   f"Відповісти на {feedback_type_text}? \\(/reply\\_feedback\\_{message.message_id}\\)")
    await context.bot.send_message(Config.OWNER_ID, text=to_dev_text, parse_mode=ParseMode.MARKDOWN_V2)

    # Inform user that feedback sent
    to_user_text = f'✅ Шик, уже надіслав [розробнику](tg://user?id={Config.OWNER_ID})!'
    await message.reply_text(escape_md2_no_links(to_user_text), parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data.clear()
    return ConversationHandler.END


async def reply_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    context.user_data['command_msg'] = message

    feedback_reply_msg_id = int(message.text.replace('/reply_feedback_', ''))

    async with get_session() as session:
        feedback_model = await get_feedback_by_msg_id(session, feedback_reply_msg_id)

    if not feedback_model:
        await message.reply_text(escape_md2(f'Дивно немає повідомлення із msg_id=`{feedback_reply_msg_id}`', ['`']),
                                 parse_mode=ParseMode.MARKDOWN_V2)
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data['feedback_reply_msg_id'] = feedback_reply_msg_id
    context.user_data['feedback_reply_user_id'] = feedback_model.user_id

    if feedback_model.feedback_type == 'bug_report':
        context.user_data['feedback_model'] = feedback_model
        response_text = "Зробимо issue з цього bug report? Або ж напиши текст цієї issue нижче:"

        context.user_data['markup_msg'] = await message.reply_text(response_text, reply_markup=make_issue_keyboard)
        return MAKE_ISSUE

    name = escape_md2(feedback_model.user.first_name)
    response_text = (f'Пишемо відповідь користувачу [{name}](tg://user?id={feedback_model.user.id}):\n\n'
                     f'{feedback_model.msg_text}\n\n')

    context.user_data['markup_msg'] = await message.reply_markdown_v2(escape_md2_no_links(response_text, ['`']),
                                                                      reply_markup=cancel_keyboard)
    return REPLY_START


async def back_to_making_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    settings_start_text = ('Не те?\nОбери з нижче наведених опцій чи зробимо issue з цього bug report?'
                           ' Або ж напиши текст для цієї issue нижче:')

    await query.edit_message_text(text=settings_start_text, reply_markup=make_issue_keyboard)

    return MAKE_ISSUE


async def feedback_reply_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    text = message.text

    feedback_reply_msg_id = context.user_data['feedback_reply_msg_id']
    feedback_reply_user_id = context.user_data['feedback_reply_user_id']
    markup_msg = context.user_data['markup_msg']

    response_text = f"У відповідь на ваше повідомлення розробник пише:\n\n"
    response_text += f"{escape_md2(text)}\n\n"
    response_text += f"Ще раз дякую за фідбек 🙃"

    await markup_msg.edit_reply_markup()

    await context.bot.send_message(chat_id=feedback_reply_user_id,
                                   text=response_text,
                                   parse_mode=ParseMode.MARKDOWN_V2,
                                   reply_to_message_id=feedback_reply_msg_id)

    async with get_session() as session:
        await mark_feedback_read(session, feedback_reply_msg_id)

    await message.reply_text('✅ Чудово, я уже відповів користувачу!')

    context.user_data.clear()
    return ConversationHandler.END


async def make_instant_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    feedback_model = context.user_data['feedback_model']
    await query.answer()

    await message.edit_text('Опрацювання...')

    resp_text = create_issue(feedback_model.user.first_name, feedback_model.msg_text)

    await message.edit_text(resp_text)

    context.user_data.clear()
    return ConversationHandler.END


async def reply_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message

    await query.answer()

    await message.edit_text('Ок, що тоді відпоівсти користувачу, надішли повідомлення нижче:',
                            reply_markup=cancel_back_keyboard)

    return REPLY_START


async def write_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    text = message.text

    feedback_model = context.user_data['feedback_model']
    markup_msg = context.user_data['markup_msg']

    await markup_msg.edit_reply_markup()

    async with get_session() as session:
        await mark_feedback_read(session, feedback_model.msg_id)

    resp_text = create_issue(feedback_model.user.first_name, text)

    await message.reply_text(resp_text)

    context.user_data.clear()
    return ConversationHandler.END


feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('feedback', start_feedback_command)],
    states={
        FEEDBACK_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(get_feedback_type, pattern=r'\w')
        ],
        GET_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_feedback, pattern='^back$'),
            MessageHandler(filters.TEXT, feedback_get_user_text)
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)

feedback_reply_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(re.compile(r'/reply_feedback_\d+')), reply_feedback)],
    states={
        REPLY_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_making_issue, pattern='^back$'),
            MessageHandler(filters.TEXT, feedback_reply_text)
        ],
        MAKE_ISSUE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(make_instant_issue, pattern='^instant_issue$'),
            CallbackQueryHandler(reply_to, pattern='^reply_to$'),
            MessageHandler(filters.TEXT, write_issue)
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)
