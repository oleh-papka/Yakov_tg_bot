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
                               mark_feedback_read, get_feedback_by_id)
from src.crud.user import create_or_update_user
from src.handlers.canel_conversation import cancel, cancel_back_keyboard
from src.utils.db_utils import get_session
from src.utils.github_utils import create_issue
from src.utils.message_utils import escape_md2, escape_md2_no_links, send_typing_action

FEEDBACK_START, GET_MESSAGE, REPLY_START, REPLY_USER, MAKE_ISSUE = 1, 2, 3, 4, 5
FEEDBACK_REPLY_COMMAND = '/reply_to_'

feedback_start_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Feedback 💬', callback_data='feedback'),
     InlineKeyboardButton('Bug report 🐛', callback_data='bug_report'),
     InlineKeyboardButton('Пропозиція 👀', callback_data='suggestion')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
])

feedback_reply_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Instant Issue 📑', callback_data='instant_issue'),
     InlineKeyboardButton('Написати Issue ✒️', callback_data='write_issue')],
    [InlineKeyboardButton('Відповісти користувачу 💬', callback_data='reply_to')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
])


@send_typing_action
async def start_feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    context.user_data['markup_msg'] = await message.reply_text('Ок, обери, що варто зробити з наведеного нижче:',
                                                               reply_markup=feedback_start_keyboard)

    return FEEDBACK_START


async def back_to_feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    elif query.data == 'bug_report':
        edited_text = ('Оу, замітив проблемки? Надішли свій bug report нижче:\n\n'
                       'P.S. Будь ласка, не забудь вказати, яка саме проблема виникла '
                       'та що зробити, щоб її відтворити, дякую. '
                       'Розробник відповість як тільки її виправить.')
    else:  # suggestion
        edited_text = 'Цікаво, маєш пропозіції, розробник буде радий почути. Напиши нижче, що хочеш запропонувати:'

    context.user_data['markup_msg'] = await message.edit_text(text=edited_text,
                                                              reply_markup=cancel_back_keyboard)

    return GET_MESSAGE


@send_typing_action
async def feedback_get_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']
    feedback_type = context.user_data['feedback_type']

    await markup_msg.edit_reply_markup()

    async with get_session() as session:
        feedback_model = await create_feedback(session=session,
                                               feedback_type=feedback_type,
                                               user_id=user.id,
                                               msg_id=message.message_id,
                                               msg_text=message.text)

    # Firstly send to developer feedback
    to_dev_text = (f"Повідомлення ({feedback_type}) від {user.name}:\n\n{message.text}\n\n"
                   f"Відповісти на {feedback_type}? ({FEEDBACK_REPLY_COMMAND}{feedback_model.id})")
    await context.bot.send_message(Config.OWNER_ID, text=escape_md2(to_dev_text), parse_mode=ParseMode.MARKDOWN_V2)

    # Inform user that feedback sent
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

    feedback_id = int(message.text.replace(FEEDBACK_REPLY_COMMAND, ''))

    async with get_session() as session:
        feedback_model = await get_feedback_by_id(session, feedback_id)

    if not feedback_model:
        await message.reply_markdown_v2(escape_md2(f'Дивно немає фідбеку із id=`{feedback_id}`', ['`']))
        context.user_data.clear()
        return ConversationHandler.END

    context.user_data['feedback_model'] = feedback_model

    response_text = f"Що зробимо з цим {feedback_model.feedback_type}?"

    context.user_data['markup_msg'] = await message.reply_text(response_text, reply_markup=feedback_reply_keyboard)
    return REPLY_START


async def make_instant_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    feedback_model = context.user_data['feedback_model']
    await query.answer()

    await message.edit_text('Опрацювання...')

    issue_text = feedback_model.msg_text + f'\n\nReply to feedback command: {FEEDBACK_REPLY_COMMAND}{feedback_model.id}'

    resp_text = create_issue(feedback_model.user.first_name, issue_text)

    await message.edit_text(escape_md2_no_links(resp_text), parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data.clear()
    return ConversationHandler.END


async def make_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    await query.answer()

    await message.edit_text('Ок тоді напиши, що б ти хотів бачити в даній issue нижче:',
                            reply_markup=cancel_back_keyboard)

    return MAKE_ISSUE


@send_typing_action
async def write_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    text = message.text

    feedback_model = context.user_data['feedback_model']
    markup_msg = context.user_data['markup_msg']

    await markup_msg.edit_reply_markup()

    async with get_session() as session:
        await mark_feedback_read(session, feedback_model.id)

    issue_text = text + f'\n\nReply to feedback command: {FEEDBACK_REPLY_COMMAND}{feedback_model.id}'

    resp_text = create_issue(feedback_model.user.first_name, issue_text)

    await message.reply_markdown_v2(escape_md2_no_links(resp_text))

    context.user_data.clear()
    return ConversationHandler.END


async def back_to_reply_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    feedback_model = context.user_data['feedback_model']

    settings_start_text = f'Що зробимо з цим {feedback_model.feedback_type}?:'

    await query.edit_message_text(text=settings_start_text, reply_markup=feedback_reply_keyboard)

    return REPLY_START


async def reply_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    await query.answer()

    feedback_model = context.user_data['feedback_model']

    name = escape_md2(feedback_model.user.first_name)
    response_text = (f'Пишемо відповідь користувачу [{name}](tg://user?id={feedback_model.user.id}) '
                     f'на {feedback_model.feedback_type}:\n\n{feedback_model.msg_text}')

    await message.edit_text(escape_md2_no_links(response_text, ['`']),
                            parse_mode=ParseMode.MARKDOWN_V2,
                            reply_markup=cancel_back_keyboard)

    return REPLY_USER


@send_typing_action
async def feedback_reply_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    text = message.text

    feedback_model = context.user_data['feedback_model']
    markup_msg = context.user_data['markup_msg']

    response_text = f"У відповідь на ваше повідомлення розробник пише:\n\n"
    response_text += f"{text}\n\n"
    response_text += f"P.S. Ще раз дякую за {feedback_model.feedback_type} 🙃"

    await markup_msg.edit_reply_markup()

    await context.bot.send_message(chat_id=feedback_model.user_id,
                                   text=escape_md2(response_text),
                                   parse_mode=ParseMode.MARKDOWN_V2,
                                   reply_to_message_id=feedback_model.msg_id)

    async with get_session() as session:
        await mark_feedback_read(session, feedback_model.id)

    await message.reply_text('✅ Чудово, я уже відповів користувачу!')

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
            CallbackQueryHandler(back_to_feedback_start, pattern='^back$'),
            MessageHandler(filters.TEXT, feedback_get_user_text)
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)

feedback_reply_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(re.compile(f'{FEEDBACK_REPLY_COMMAND}\d+')), reply_feedback)],
    states={
        REPLY_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(make_instant_issue, pattern='^instant_issue$'),
            CallbackQueryHandler(make_issue, pattern='^write_issue$'),
            CallbackQueryHandler(reply_to, pattern='^reply_to$'),
        ],
        REPLY_USER: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_reply_start, pattern='^back$'),
            MessageHandler(filters.TEXT, feedback_reply_text)
        ],
        MAKE_ISSUE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_reply_start, pattern='^back$'),
            MessageHandler(filters.TEXT, write_issue)
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)
