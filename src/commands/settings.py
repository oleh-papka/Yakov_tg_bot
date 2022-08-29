import re

from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, Filters, \
    CallbackContext

from config import Config
from crud.city import get_city_by_name, get_city_by_user, create_city
from crud.crypto_currency import get_crypto_by_user, get_crypto_by_abbr
from crud.user import auto_create_user, get_user, update_user
from handlers.canel_conversation import cancel, cancel_keyboard
from utils.db_utils import create_session
from utils.message_utils import send_chat_action
from utils.time_utils import timezone_offset_repr
from utils.weather_utils import get_city_info, get_sinoptik_url

CONV_START, USER_CITY_CHANGE, USER_CITY_TIMEZONE_CHECK, USER_TIMEZONE_CHANGE, USER_CRYPTO_CHANGE = 1, 2, 3, 4, 5

main_settings_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Змінити місто 🏙️', callback_data='city')],
    [InlineKeyboardButton('Змінити часовий пояс 🌐', callback_data='timezone')],
    [InlineKeyboardButton('Змінити крипто валюти 🪙', callback_data='crypto')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
], )


@create_session
@send_chat_action(ChatAction.TYPING)
def settings(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    auto_create_user(db, user)
    context.user_data['reply_msg_id'] = message.message_id

    context.user_data['reply_markup'] = message.reply_text('Бажаєш змінити щось?\nОбери з нижче наведених опцій:',
                                                           reply_markup=main_settings_keyboard)

    return CONV_START


@create_session
def user_city_check(update: Update, context: CallbackContext, db):
    query = update.callback_query
    message = query.message
    query.answer()
    context.user_data['reply_msg_id'] = message.message_id

    msg = '🆗 Обрано зміну міста для прогнозу погоди.\n\n'

    if row := get_city_by_user(db, query.from_user.id):
        city_model, user_model = row[0], row[1]
        msg += f'⚠ В тебе уже вказане місто - {city_model.name}. Ти справді хочеш його змінити?\n\n' \
               f'Для зміни надішли назву міста у наступному повідомленні.'
    else:
        msg += 'Надішли мені назву міста у наступному повідомленні, щоб встановити відповідне.'

    msg += '\n\nP.S. Будь ласка вказуй назву міста українською мовою, якщо можливо, ' \
           'я не досконало знаю англійську, тому можуть виникати проблеми...'

    context.user_data['message_with_markup'] = message.edit_text(text=msg, reply_markup=cancel_keyboard)

    return USER_CITY_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_city_change(update: Update, context: CallbackContext, db):
    message = update.message

    message_with_markup = context.user_data['message_with_markup']
    message_with_markup.edit_reply_markup()
    context.user_data['reply_msg_id'] = message.message_id

    err_msg = '⚠ Cхоже назва міста вказана не вірно, я не можу занйти такого міста, спробуй ще раз.'
    warning_msg = '\n\n⚠ Hey, you wrote city name not in Cyrillic, ' \
                  'so I cannot return weather picture on /weather command.\n\n' \
                  'Я ж просив писати українською, тепер тобі доведеться ' \
                  'бачити лиш текст замість красивої картинки. Сподіваюсь це тебе влаштує,' \
                  'для того, щоб змінити місто достатньо обрати відповідний пункт в команді /settings'

    user_input = message.text.strip().capitalize()

    if re.search(r'\d|[.^$*+?\[\](){}\\,/!@#%&|~`\'\";:_=<>]', user_input) or len(user_input) > 20:
        context.user_data['message_with_markup'] = message.reply_text(err_msg, reply_markup=cancel_keyboard)
        return USER_CITY_CHANGE

    user_model = get_user(db, message.from_user.id)
    city_data = get_city_info(user_input)

    if not city_data:
        context.user_data['message_with_markup'] = message.reply_text(err_msg, reply_markup=cancel_keyboard)
        return USER_CITY_CHANGE

    city_name_eng = city_data['name']
    msg = f'✅ Зроблено, твоє місто тепер - {city_name_eng}.'
    city_model = get_city_by_name(db, city_name_eng)

    if city_model:
        if city_model.name == user_model.city[0].name:
            msg = '❕ Так це ж те саме місто, жодних змін не вношу 🙃\n\n Потрібно змінити ще щось?'

        if not city_model.url:
            if url := get_sinoptik_url(user_input):
                city_model.url = url
            else:
                msg += warning_msg

        user_model.city = [city_model]
        db.commit()

        message.reply_text(msg, reply_markup=main_settings_keyboard)
        return CONV_START
    else:
        sinoptik_base_url = get_sinoptik_url(user_input)
        city_model = create_city(db,
                                 owm_id=city_data['id'],
                                 name=city_name_eng,
                                 lat=city_data['lat'],
                                 lon=city_data['lon'],
                                 url=sinoptik_base_url,
                                 timezone_offset=city_data['timezone_offset'])

        if not city_model.url:
            msg += warning_msg

        user_model.city = [city_model]
        db.commit()

    city_changed_message = message.reply_text(msg, reply_to_message_id=message.message_id)

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
        city_changed_message.edit_text(msg, reply_markup=approve_keyboard)
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
    query.answer()
    message = query.message

    context.user_data['reply_msg_id'] = message.message_id
    context.user_data['markup_msg'] = message

    row = get_city_by_user(db, query.from_user.id)
    city_model, user_model = row[0], row[1]

    msg = '🆗 Обрано зміну часового поясу.\n\n' \
          'Поточні дані часового поясу:\n'
    if city_model:
        msg += f'{Config.SPACING}У місті {city_model.name}: {timezone_offset_repr(city_model.timezone_offset)}\n'

    msg += f'{Config.SPACING}Вказаний в профілі: {timezone_offset_repr(user_model.timezone_offset)}\n\n' \
           f'Для зміни часового поясу надішли відповідний у наступному повідомленні (Приклад: +3).'

    message.edit_text(text=msg, reply_markup=cancel_keyboard)
    return USER_TIMEZONE_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_timezone_change(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    user_input = message.text.strip()
    markup_msg = context.user_data['markup_msg']
    markup_msg.edit_reply_markup()

    if re.match(r'^[+|-]?[1-9][0-2]?$', user_input) and abs(int(user_input)) in range(1, 13):
        timezone_offset = int(user_input) * 3600
    else:
        msg = '⚠ Cхоже часовий пояс вказано не вірно, спробуй ще раз.'
        context.user_data['markup_msg'] = message.reply_text(text=msg, reply_markup=cancel_keyboard)
        return USER_TIMEZONE_CHANGE

    context.user_data['reply_msg_id'] = message.message_id
    update_user(db, user, {'timezone_offset': timezone_offset})

    msg = f'✅ Зроблено, твій часовий пояс тепер {timezone_offset_repr(timezone_offset)}'
    message.reply_text(text=msg, reply_markup=None)
    return ConversationHandler.END


def compose_crypto_keyboard(data: list | None = None):
    data = [] if data is None else data

    btc = '☑' if 'BTC' in data else '❌'
    eth = '☑' if 'ETH' in data else '❌'
    bnb = '☑' if 'BNB' in data else '❌'
    xrp = '☑' if 'XRP' in data else '❌'
    doge = '☑' if 'DOGE' in data else '❌'
    sol = '☑' if 'SOL' in data else '❌'

    crypto_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f'BTC {btc}', callback_data='BTC'),
            InlineKeyboardButton(f'ETH {eth}', callback_data='ETH'),
            InlineKeyboardButton(f'BNB {bnb}', callback_data='BNB'),
        ],
        [
            InlineKeyboardButton(f'XRP {xrp}', callback_data='XRP'),
            InlineKeyboardButton(f'DOGE {doge}', callback_data='DOGE'),
            InlineKeyboardButton(f'SOL {sol}', callback_data='SOL'),
        ],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ])

    return crypto_keyboard


@create_session
def user_crypto_check(update: Update, context: CallbackContext, db):
    query = update.callback_query
    message = query.message
    query.answer()
    context.user_data['reply_msg_id'] = message.message_id

    msg = '🆗 Обрано зміну криптовалют.\n\nМенеджемент криптою можеш проводити нижче, щоб відстежувати відповідну.'

    if crypto_models := get_crypto_by_user(db, update.effective_user.id):
        data = [model.abbr for model in crypto_models]
    else:
        data = []

    crypto_keyboard = compose_crypto_keyboard(data)

    context.user_data['message_with_markup'] = message.edit_text(text=msg, reply_markup=crypto_keyboard)
    context.user_data['crypto_data'] = data
    return USER_CRYPTO_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_crypto_change(update: Update, context: CallbackContext, db):
    query = update.callback_query
    query.answer()
    message = query.message

    user_model = get_user(db, update.effective_user.id)

    user_choice = query.data
    data = context.user_data['crypto_data']
    model = get_crypto_by_abbr(db, user_choice)
    if user_choice in data:
        data.remove(user_choice)
        user_model.crypto_currency.remove(model)
    else:
        data.extend([user_choice])
        user_model.crypto_currency.append(model)

    db.commit()

    crypto_keyboard = compose_crypto_keyboard(data)
    message.edit_reply_markup(crypto_keyboard)

    context.user_data['crypto_data'] = data

    return USER_CRYPTO_CHANGE


settings_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings)],
    states={
        CONV_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(user_city_check, pattern='^city$'),
            CallbackQueryHandler(user_timezone_check, pattern='^timezone$'),
            CallbackQueryHandler(user_crypto_check, pattern='^crypto$'),
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
        ],
        USER_CRYPTO_CHANGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(user_crypto_change, pattern=r'\w')
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel)
    ],
    conversation_timeout=300.0
)
