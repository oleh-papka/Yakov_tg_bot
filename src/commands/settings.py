import re

from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, Filters, \
    CallbackContext

from config import Config
from crud.city import get_city_by_name, get_city_by_user, create_city
from crud.user import auto_create_user, get_user, update_user
from handlers.canel_conversation import cancel
from utils.db_utils import create_session
from utils.message_utils import send_chat_action
from utils.time_utils import timezone_offset_repr
from utils.weather_utils import ping_city_sinoptik, ping_city_owm_api

CONV_START, USER_CITY_CHANGE, USER_CITY_TIMEZONE_CHECK, USER_TIMEZONE_CHANGE = 1, 2, 3, 4

main_settings_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Змінити місто 🏙️', callback_data='city')],
    [InlineKeyboardButton('Змінити часовий пояс 🌐', callback_data='timezone')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
], )
cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]])


@create_session
@send_chat_action(ChatAction.TYPING)
def settings(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    auto_create_user(db, user)
    context.user_data['reply_msg_id'] = message.message_id

    message.reply_text('Бажаєте змінити щось?\nОберіть з нижче наведених опцій:',
                       reply_markup=main_settings_keyboard)

    return CONV_START


@create_session
def user_city_check(update: Update, context: CallbackContext, db):
    query = update.callback_query
    user = query.from_user
    query.answer()
    context.user_data['reply_msg_id'] = query.message.message_id

    msg = '🆗 Обрано зміну міста для прогнозу погоди.\n\n'

    if row := get_city_by_user(db, user.id):
        city_model, user_model = row[0], row[1]
        msg += f'⚠ В тебе уже вказане місто - {city_model.name}. Ти справді хочеш його змінити?\n\n' \
               f'Для зміни надішли назву міста у наступному повідомленні.'

        context.user_data['city_model'] = city_model
    else:
        msg += 'Надішли мені назву міста у наступному повідомленні, щоб встановити відповідне.'

    msg += '\n\nP.S. Будь ласка вказуй назву міста українською мовою, якщо можливо, ' \
           'я не досконало знаю англійську, тому можуть виникати проблеми...'

    message_with_markup = query.edit_message_text(text=msg, reply_markup=cancel_keyboard)
    context.user_data['message_with_markup'] = message_with_markup

    return USER_CITY_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_city_change(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    city_name = message.text.strip().capitalize()
    message_with_markup = context.user_data['message_with_markup']
    message_with_markup.edit_reply_markup(reply_markup=None)
    context.user_data['reply_msg_id'] = message.message_id

    user_city_model = context.user_data.get('city_model')
    user_model = get_user(db, user.id)

    if user_city_model and user_city_model.name == city_name:
        msg = '❕ Так це ж те саме місто, жодних змін не вношу 🙃\n\n Потрібно змінити ще щось?'
        message.reply_text(msg, reply_markup=main_settings_keyboard)
        return CONV_START

    city_data = ping_city_owm_api(city_name)
    city_name_eng = city_data['name']

    if not city_data:
        msg = '⚠ Cхоже назва міста вказана не вірно, я не можу занйти такого міста, спробуй ще раз.'
        message.reply_text(msg, reply_markup=cancel_keyboard)
        return USER_CITY_CHANGE

    city_model = get_city_by_name(db, city_name_eng)
    if not city_model:
        timezone_offset = city_data['timezone_offset']
        sinoptik_base_url = ping_city_sinoptik(city_name)
        city_model = create_city(db,
                                 name=city_name_eng,
                                 lat=city_data['lat'],
                                 lon=city_data['lon'],
                                 url=sinoptik_base_url,
                                 timezone_offset=timezone_offset
                                 )

    user_model.city = [city_model]
    db.commit()

    msg = f'✅ Зроблено, твоє місто тепер - {city_model.name}.'
    city_change_message = message.reply_text(msg, reply_to_message_id=message.message_id)

    city_timezone_offset = city_model.timezone_offset
    if city_timezone_offset and (city_timezone_offset != user_model.timezone_offset):
        msg += '\n\n❕ У тебе і цього міста різні часові пояси, змінити на відповідний місту часовий пояс?'
        approve_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f'Змінити на "{timezone_offset_repr(city_timezone_offset)}"',
                                  callback_data='change_to_city')],
            [InlineKeyboardButton('Детальні налаштування 🌐', callback_data='change')],
            [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
        ])

        context.user_data['city_model'] = city_model
        city_change_message.edit_text(msg, reply_markup=approve_keyboard)
        return USER_CITY_TIMEZONE_CHECK

    context.user_data.clear()

    return ConversationHandler.END


@create_session
def change_timezone_to_city(update: Update, context: CallbackContext, db):
    query = update.callback_query
    user = query.from_user
    query.answer()
    context.user_data['reply_msg_id'] = query.message.message_id

    city_model = context.user_data.get('city_model')
    timezone_offset = city_model.timezone_offset

    user_data = {
        'timezone_offset': timezone_offset
    }
    update_user(db, user, user_data)

    msg = f'✅ Зроблено, твій часовий пояс тепер відповідає вказаному місту ' \
          f'{city_model.name} ({timezone_offset_repr(city_model.timezone_offset)}).'
    query.edit_message_text(text=msg, reply_markup=None)
    return ConversationHandler.END


@create_session
def user_timezone_check(update: Update, context: CallbackContext, db):
    query = update.callback_query
    user = query.from_user
    query.answer()
    context.user_data['reply_msg_id'] = query.message.message_id

    city_model = context.user_data.get('city_model')
    user_model = context.user_data.get('user_model')

    if not user_model or not city_model:
        row = get_city_by_user(db, user.id)
        city_model, user_model = row[0], row[1]

    msg = '🆗 Обрано зміну часового поясу.\n\n' \
          'Поточні дані:\n'

    if city_model:
        msg += f'{Config.SPACING}У місті {city_model.name}: {timezone_offset_repr(city_model.timezone_offset)}\n'

    msg += f'{Config.SPACING}Вказаний в профілі: {timezone_offset_repr(user_model.timezone_offset)}\n\n' \
           f'Для зміни часового поясу надішли відповідний у наступному повідомленні (Приклад: +3).'

    query.edit_message_text(text=msg, reply_markup=cancel_keyboard)
    return USER_TIMEZONE_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_timezone_change(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    timezone_offset = int(message.text.strip()) * 3600
    context.user_data['reply_msg_id'] = message.message_id

    user_data = {
        'timezone_offset': timezone_offset
    }

    update_user(db, user, user_data)

    msg = f'✅ Зроблено, твій часовий пояс тепер {timezone_offset_repr(timezone_offset)}.'
    message.reply_text(text=msg, reply_markup=None)
    return ConversationHandler.END


settings_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings)],
    states={
        CONV_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(user_city_check, pattern='^city$'),
            CallbackQueryHandler(user_timezone_check, pattern='^timezone$'),
        ],
        USER_CITY_CHANGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(Filters.regex(re.compile(r'^/')), cancel),
            MessageHandler(Filters.text, user_city_change)
        ],
        USER_CITY_TIMEZONE_CHECK: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(user_timezone_check, pattern='^change$'),
            CallbackQueryHandler(change_timezone_to_city, pattern='^change_to_city$'),
        ],
        USER_TIMEZONE_CHANGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(Filters.regex(re.compile(r'^/')), cancel),
            MessageHandler(Filters.text, user_timezone_change)
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel)
    ],
    conversation_timeout=300.0
)
