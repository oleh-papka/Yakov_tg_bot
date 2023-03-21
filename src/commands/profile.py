import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, \
    filters

from src.config import Config
from src.crud.feedback import get_unread_feedbacks
from src.crud.user import create_or_update_user, get_user_by_id, get_all_users, update_user
from src.handlers.canel_conversation import cancel, cancel_keyboard
from src.utils.db_utils import get_session
from src.utils.message_utils import escape_md2, send_typing_action
from src.utils.time_utils import UserTime

PROFILE_START, GET_MESSAGE, SEND_MESSAGE = 1, 2, 3


@send_typing_action
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = message.from_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    resp_keyboard = [
        [InlineKeyboardButton('Мої дані 📊', callback_data='user_data')],
        [InlineKeyboardButton('🚫 Відміна', callback_data='cancel')]
    ]

    if user.id == Config.OWNER_ID:
        additional_keys = [
            InlineKeyboardButton('Написати усім 💬', callback_data='send_to_all'),
            InlineKeyboardButton('Тестувальнику 👤', callback_data='send_to_tester')
        ]
        feedback_key = [InlineKeyboardButton('Не прочитані feedbacks 📃', callback_data='get_feedbacks')]

        resp_keyboard.insert(1, additional_keys)
        resp_keyboard.insert(2, feedback_key)

    reply_keyboard = InlineKeyboardMarkup(resp_keyboard)

    profile_start_text = f'{user.name}, у цій команді багато трішки різного, обирай нижче:'
    context.user_data['markup_msg'] = await message.reply_text(profile_start_text, reply_markup=reply_keyboard)

    return PROFILE_START


async def user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']
    await query.answer()

    await markup_msg.edit_reply_markup()

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        users_city_model = user_model.city

    since = user_model.joined.strftime('%d/%m/%Y')
    city = 'Немає інформації' if not users_city_model else users_city_model.name
    crypto_curr = '*, *'.join([crypto.abbr for crypto in user_model.crypto_currency])
    crypto_curr = 'Немає інформації' if not crypto_curr else crypto_curr
    curr = '*, *'.join([curr.name.upper() for curr in user_model.currency])
    curr = 'Немає інформації' if not curr else curr

    user_timezone_repr = UserTime.offset_repr(user_model.timezone_offset)
    profile_text = f'🆗 Гаразд, ось усі твої дані: \n\n'
    profile_text += f'Місто: *{city}*\n'
    profile_text += f'Часовий пояс: *{user_timezone_repr}*\n'
    profile_text += f'Мова: *{user_model.language_code}*\n'
    profile_text += f'Криптовалюти: *{crypto_curr}*\n'
    profile_text += f'Валюти: *{curr}*\n'
    profile_text += f'Користувач із: _{since}_\n\n'
    profile_text += 'Для зміни та налаштування - /settings'

    await query.edit_message_text(escape_md2(profile_text, ['*', '_']),
                                  parse_mode=ParseMode.MARKDOWN_V2,
                                  reply_markup=None)

    context.user_data.clear()

    return ConversationHandler.END


async def get_feedbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    markup_msg = context.user_data['markup_msg']
    await query.answer()

    await markup_msg.edit_reply_markup()

    async with get_session() as session:
        feedbacks_unread = await get_unread_feedbacks(session)

    feedbacks_text = 'Ось усі не прочитані фідбеки:\n\n' if feedbacks_unread else 'Немає непрочитаних фідбеків!'

    for feedback in feedbacks_unread:
        feedbacks_text += (f'{Config.FEEDBACK_REPLY_COMMAND}{feedback.id}{Config.SPACING}'
                           f'({feedback.feedback_type.replace("_", " ")})\n')

    await query.edit_message_text(feedbacks_text)

    context.user_data.clear()

    return ConversationHandler.END


async def send_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    markup_msg = context.user_data['markup_msg']
    await query.answer()

    await markup_msg.edit_reply_markup()

    send_to_text = '🆗 Гаразд, будемо сповіщати {}\n\nНадішли текст цього повідомлення нижче:'

    if query.data == 'send_to_all':
        context.user_data['send_to_all'] = True
        send_to_text = send_to_text.format('усіх користувачів')
    else:
        context.user_data['send_to_all'] = False
        send_to_text = send_to_text.format('тестувальника')

    context.user_data['send_to_query'] = query

    await query.edit_message_text(send_to_text, reply_markup=cancel_keyboard)

    return GET_MESSAGE


@send_typing_action
async def message_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    context.user_data['message_text'] = message.text

    if query := context.user_data.get('send_to_query'):
        await query.edit_message_reply_markup()

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

    return SEND_MESSAGE


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    msg_text = context.user_data['message_text']

    sending_text = '🆗 Уже надсилаю...'
    await query.edit_message_text(sending_text, reply_markup=None)

    if context.user_data.get('send_to_all'):
        async with get_session() as session:
            users = await get_all_users(session, True)

        users_count = len(users)
        decr = 0

        for number, user in enumerate(users):
            try:
                await context.bot.send_message(user.id, msg_text)
            except:
                async with get_session() as session:
                    await update_user(session, user, {'active': False})
                users_count -= 1
                decr -= 1

            number += decr
            tmp_msg = sending_text + f'\n\nНадіслано {number + 1} із {users_count}'
            await query.edit_message_text(tmp_msg)

        sending_text = f'✅ Єєєєй! Уже завершив, усі ({users_count}) користувачі отримали твоє повідомлення.'
    else:
        user_id = Config.TESTER_ID
        context.bot.send_message(user_id, msg_text)
        sending_text = f'✅ Єєєєй! Уже надіслав твоє повідомлення тестувальнику!'

    await query.edit_message_text(sending_text)

    context.user_data.clear()
    return ConversationHandler.END


async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    edit_text = '🆗 Надішли у наступному повідомленні відповідно змінене.'
    await query.edit_message_text(edit_text, reply_markup=None)

    if 'send_to_query' in context.user_data:
        del context.user_data['send_to_query']

    return GET_MESSAGE


profile_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('profile', profile)],
    states={
        PROFILE_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(send_to, pattern='^send_to'),
            CallbackQueryHandler(get_feedbacks, pattern='^get_feedbacks$'),
            CallbackQueryHandler(user_data, pattern='^user_data$')
        ],
        GET_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(filters.COMMAND, cancel),
            MessageHandler(filters.TEXT, message_check)
        ],
        SEND_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(send_message, pattern='^confirm$'),
            CallbackQueryHandler(edit_message, pattern='^edit$')
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=600.0
)
