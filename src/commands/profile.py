import re

from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import MessageHandler, CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, \
    CallbackContext

from config import Config
from crud.city import get_city_by_user
from crud.user import auto_create_user, get_all_users, update_user
from handlers import cancel
from handlers.canel_conversation import cancel_keyboard
from utils.db_utils import create_session
from utils.message_utils import send_chat_action, escape_str_md2
from utils.time_utils import timezone_offset_repr

CONV_START, GET_MESSAGE, SEND_MESSAGE = 1, 2, 3


@create_session
@send_chat_action(ChatAction.TYPING)
def profile(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    auto_create_user(db, user)
    context.user_data.clear()

    resp_keyboard = [
        [InlineKeyboardButton('Мої дані 📊', callback_data='user_data')],
        [InlineKeyboardButton('🚫 Відміна', callback_data='cancel')]
    ]

    if user.id == Config.OWNER_ID:
        additional_keys = [
            InlineKeyboardButton('Написати усім 💬', callback_data='send_to_all'),
            InlineKeyboardButton('Тестувальнику 👤', callback_data='send_to_tester')
        ]
        resp_keyboard.insert(1, additional_keys)

    reply_keyboard = InlineKeyboardMarkup(resp_keyboard)
    msg = f'{user.name}, у цій команді багато трішки різного, обирай нижче:'
    reply_message = message.reply_text(msg, reply_markup=reply_keyboard)
    context.user_data['reply_msg_id'] = reply_message.message_id

    return CONV_START


@create_session
def user_data(update: Update, context: CallbackContext, db):
    query = update.callback_query
    user = update.effective_user
    query.answer()

    user_model = auto_create_user(db, user)
    since = user_model.joined.strftime('%d/%m/%Y')
    city = get_city_by_user(db, user.id)
    city = 'Немає інформації' if not city else city[0].name

    msg = f'🆗 Гаразд, ось усі твої дані: \n\n'
    msg += f'Місто: *{city}*\n'
    msg += f'Часовий пояс: *{timezone_offset_repr(user_model.timezone_offset)}*\n'
    msg += f'Мова: *{user_model.language_code}*\n'
    msg += f'Користувач із: _{since}_\n\n'
    msg += 'Для зміни та налаштування - /settings'

    query.edit_message_text(escape_str_md2(msg, ['*', '_']), parse_mode=ParseMode.MARKDOWN_V2, reply_markup=None)
    context.user_data.clear()

    return ConversationHandler.END


def send_to(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    msg = '🆗 Гаразд, будемо сповіщати {}\n\nНадішли текст цього повідомлення нижче:'

    if query.data == 'send_to_all':
        context.user_data['send_to_all'] = True
        msg = msg.format('усіх користувачів')
    else:
        context.user_data['send_to_all'] = False
        msg = msg.format('тестувальника')

    context.user_data['send_to_query'] = query

    query.edit_message_text(msg, reply_markup=cancel_keyboard)

    return GET_MESSAGE


@send_chat_action(ChatAction.TYPING)
def message_check(update: Update, context: CallbackContext):
    message = update.message
    context.user_data['message_text'] = message.text

    if query := context.user_data.get('send_to_query'):
        query.edit_message_reply_markup()

    confirmation_keyboard = [
        [
            InlineKeyboardButton('Підтвердити ✅', callback_data='confirm'),
            InlineKeyboardButton('Редагувати 📝', callback_data='edit')
        ],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ]

    reply_keyboard = InlineKeyboardMarkup(confirmation_keyboard)

    reply_message = message.reply_text('Впевнений, надіслати дане повідомлення?',
                                       reply_markup=reply_keyboard,
                                       reply_to_message_id=message.message_id)

    context.user_data['reply_msg_id'] = reply_message.message_id

    return SEND_MESSAGE


@create_session
def send_message(update: Update, context: CallbackContext, db):
    query = update.callback_query
    query.answer()
    msg_text = context.user_data['message_text']

    msg = '🆗 Уже надсилаю...'
    query.edit_message_text(msg, reply_markup=None)

    if context.user_data.get('send_to_all'):
        users = get_all_users(db, True)
        users_count = len(users)
        decr = 0

        for number, user in enumerate(users):
            try:
                context.bot.send_message(user.id, msg_text)
            except:
                update_user(db, user, {'active': False})
                users_count -= 1
                decr -= 1

            number += decr
            tmp_msg = msg + f'\n\nНадіслано {number + 1} із {users_count}'
            query.edit_message_text(tmp_msg)

        msg = f'✅ Єєєєй! Уже завершив, усі ({users_count}) користувачі отримали твоє повідомлення.'
    else:
        user_id = Config.TESTER_ID
        context.bot.send_message(user_id, msg_text)
        msg = f'✅ Єєєєй! Уже надіслав твоє повідомлення тестувальнику!'

    query.edit_message_text(msg)

    return ConversationHandler.END


def edit_message(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    msg = '🆗 Надішли у наступному повідомленні відповідно змінене.'
    query.edit_message_text(msg, reply_markup=None)

    if 'send_to_query' in context.user_data:
        del context.user_data['send_to_query']

    return GET_MESSAGE


profile_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('profile', profile)],
    states={
        CONV_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(send_to, pattern='^send_to'),
            CallbackQueryHandler(user_data, pattern='^user_data$')
        ],
        GET_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(Filters.regex(re.compile(r'^/')), cancel),
            MessageHandler(Filters.text, message_check)
        ],
        SEND_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(send_message, pattern='^confirm$'),
            CallbackQueryHandler(edit_message, pattern='^edit$')
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel)
    ],
    conversation_timeout=600.0
)
