import re

from sqlalchemy.orm import Session
from telegram import (ChatAction,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup,
                      Update)
from telegram.ext import (ConversationHandler,
                          CallbackQueryHandler,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext)

from config import Config
from crud import city as city_models
from crud.crypto_currency import get_crypto_by_user_id, get_crypto_by_abbr
from crud.currency import get_curr_by_user_id, get_curr_by_name
from crud.user import create_or_update_user, get_user, update_user
from handlers.canel_conversation import cancel, cancel_keyboard
from models.errors import CityFetchError, SinoptikURLFetchError
from utils.db_utils import create_session
from utils.message_utils import send_chat_action
from utils.time_utils import UserTime
from utils.weather_utils import OpenWeatherMapAPI, SinoptikScraper

(CONV_START,
 USER_CITY_CHANGE,
 USER_CITY_TIMEZONE_CHECK,
 USER_TIMEZONE_CHANGE,
 USER_CRYPTO_CHANGE,
 USER_CURR_CHANGE) = 1, 2, 3, 4, 5, 6

main_settings_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Місто 🏙️', callback_data='city')],
    [InlineKeyboardButton('Часовий пояс 🌐', callback_data='timezone')],
    [InlineKeyboardButton('Крипто валюти 🪙', callback_data='crypto')],
    [InlineKeyboardButton('Фіатні валюти 🇺🇦', callback_data='curr')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
], )


@create_session
@send_chat_action(ChatAction.TYPING)
def settings(update: Update, context: CallbackContext, db: Session):
    message = update.message
    user = message.from_user
    context.user_data['cancel_reply_msg_id'] = message.message_id

    create_or_update_user(db, user)

    context.user_data['cancel_reply_message'] = message.message_id
    context.user_data['cancel_reply_markup_msg'] = message.reply_text(
        'Бажаєш налаштувати щось?\nОбери з нижче наведених опцій:', reply_markup=main_settings_keyboard)

    return CONV_START


@create_session
def user_city_check(update: Update, context: CallbackContext, db: Session):
    query = update.callback_query
    user = update.effective_user
    message = query.message
    query.answer()

    msg = '🆗 Обрано зміну міста для прогнозу погоди.\n\n'

    if row := city_models.get_user_city(db, user.id):
        city_model, user_model = row[0], row[1]
        msg += (f'⚠ В тебе уже вказане місто - {city_model.name}. Ти справді хочеш його змінити?\n\n'
                'Для зміни надішли назву міста або пряме посилання на нього '
                'з ua.sinoptik.ua у наступному повідомленні.')
    else:
        msg += ('Надішли мені назву міста або пряме посилання на нього з ua.sinoptik.ua '
                'у наступному повідомленні, щоб встановити відповідне.')

    msg += ('\n\nP.S. Якщо виникають проблеми - спробуй вказати місто українською, '
            'або ж спробуй через посилання, у зворотньому випадку напиши про це розробнику - /feedback')

    context.user_data['msg_with_markup'] = message.edit_text(text=msg, reply_markup=cancel_keyboard)

    return USER_CITY_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_city_change(update: Update, context: CallbackContext, db: Session):
    message = update.message
    user = update.effective_user
    msg_with_markup = context.user_data['msg_with_markup']
    context.user_data['cancel_reply_msg_id'] = message.message_id

    msg_with_markup.edit_reply_markup()
    user_input = message.text.strip().capitalize()

    wrong_symbols_error_msg = '⚠ Глузуєш? Бо, я щось глибоко сумніваюсь, що є таке місто...'
    if re.search(r'\d|[.^$*+?\[\](){}\\,/!@#%&|~`\'\";:_=<>]', user_input) or len(user_input) > 25:
        context.user_data['msg_with_markup'] = message.reply_text(wrong_symbols_error_msg, reply_markup=cancel_keyboard)
        return USER_CITY_CHANGE

    try:
        city_data = OpenWeatherMapAPI.get_city(user_input)
    except CityFetchError:
        city_not_found_error_msg = '⚠ Cхоже назва міста вказана не вірно(або я дурний), бо не можу занйти такого міста.'
        context.user_data['msg_with_markup'] = message.reply_text(city_not_found_error_msg,
                                                                  reply_markup=cancel_keyboard)
        return USER_CITY_CHANGE

    user_model = get_user(db, user.id)

    city_name_local = city_data['local_name']
    city_name_eng = city_data['name']
    msg = f'✅ Зроблено, твоє місто тепер - {city_name_local}.'

    if city_model := city_models.get_city(db, city_name_eng):
        if city_model.name == user_model.city[0].name:
            msg = '❕ Так це ж те саме місто, жодних змін не вношу 🙃\n\n Потрібно змінити ще щось?'

        if not city_model.sinoptik_url:
            try:
                url = SinoptikScraper.get_url(city_name_local)
                city_model.sinoptik_url = url
            except SinoptikURLFetchError:
                msg += '\n\nНе вдалось додати дані з ua.sinoptik.ua!'

        user_model.city = [city_model]
        db.commit()

        message.reply_text(msg, reply_markup=main_settings_keyboard)
        return CONV_START
    else:
        sinoptik_base_url = SinoptikScraper.get_url(city_name_local)
        city_model = city_models.create_city(db,
                                             owm_id=city_data['id'],
                                             name=city_name_eng,
                                             local_name=city_name_local,
                                             lat=city_data['lat'],
                                             lon=city_data['lon'],
                                             sinoptik_url=sinoptik_base_url,
                                             timezone_offset=city_data['timezone_offset'])

        user_model.city = [city_model]
        db.commit()

    city_changed_message = message.reply_text(msg, reply_to_message_id=message.message_id)

    city_timezone_offset = city_model.timezone_offset
    if city_timezone_offset and (city_timezone_offset != user_model.timezone_offset):
        msg += '\n\n❕ У тебе і цього міста різні часові пояси, змінити на відповідний місту часовий пояс?'
        approve_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f'Змінити на "{UserTime.offset_repr(city_timezone_offset)}"',
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

    city_model = context.user_data.get('city_model')
    timezone_offset = city_model.timezone_offset

    user_data = {
        'timezone_offset': timezone_offset
    }
    update_user(db, user, user_data)

    msg = f'✅ Зроблено, твій часовий пояс тепер відповідає вказаному місту ' \
          f'{city_model.name} ({UserTime.offset_repr(city_model.timezone_offset)}).'
    query.edit_message_text(text=msg, reply_markup=None)

    context.user_data.clear()
    return ConversationHandler.END


@create_session
def user_timezone_check(update: Update, context: CallbackContext, db):
    query = update.callback_query
    query.answer()
    message = query.message

    context.user_data['cancel_reply_msg_id'] = message.message_id
    context.user_data['cancel_reply_markup_msg_id'] = message.message_id

    row = city_models.get_user_city(db, query.from_user.id)
    city_model, user_model = row[0], row[1]

    msg = '🆗 Обрано зміну часового поясу.\n\n' \
          'Поточні дані часового поясу:\n'
    if city_model:
        msg += f'{Config.SPACING}У місті {city_model.name}: {UserTime.offset_repr(city_model.timezone_offset)}\n'

    msg += f'{Config.SPACING}Вказаний в профілі: {UserTime.offset_repr(user_model.timezone_offset)}\n\n' \
           f'Для зміни часового поясу надішли відповідний у наступному повідомленні (Приклад: +3).'

    message.edit_text(text=msg, reply_markup=cancel_keyboard)

    return USER_TIMEZONE_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_timezone_change(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    user_input = message.text.strip()

    msg_with_markup = context.user_data['msg_with_markup']
    msg_with_markup.edit_reply_markup()

    if re.match(r'^[+|-]?[1-9][0-2]?$', user_input) and abs(int(user_input)) in range(1, 13):
        timezone_offset = int(user_input) * 3600
    else:
        msg = '⚠ Cхоже часовий пояс вказано не вірно, спробуй ще раз.'
        context.user_data['msg_with_markup'] = message.reply_text(text=msg, reply_markup=cancel_keyboard)
        return USER_TIMEZONE_CHANGE

    context.user_data['cancel_reply_msg_id'] = message.message_id
    update_user(db, user, {'timezone_offset': timezone_offset})

    msg = f'✅ Зроблено, твій часовий пояс тепер {UserTime.offset_repr(timezone_offset)}'
    message.reply_text(text=msg, reply_markup=None)

    context.user_data.clear()
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
    context.user_data['cancel_reply_msg_id'] = message.message_id

    msg = '🆗 Обрано зміну криптовалют.\n\nМенеджемент криптою можеш проводити нижче, щоб відстежувати відповідну.'

    if crypto_models := get_crypto_by_user_id(db, update.effective_user.id):
        data = [model.abbr for model in crypto_models]
    else:
        data = []

    crypto_keyboard = compose_crypto_keyboard(data)

    context.user_data['msg_with_markup'] = message.edit_text(text=msg, reply_markup=crypto_keyboard)
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


def compose_curr_keyboard(data: list | None = None):
    data = [] if data is None else data

    usd = '☑' if 'usd' in data else '❌'
    eur = '☑' if 'eur' in data else '❌'
    pln = '☑' if 'pln' in data else '❌'
    gbp = '☑' if 'gbp' in data else '❌'

    curr_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f'USD {usd}', callback_data='usd'),
            InlineKeyboardButton(f'EUR {eur}', callback_data='eur'),
            InlineKeyboardButton(f'PLN {pln}', callback_data='pln'),
            InlineKeyboardButton(f'GBP {gbp}', callback_data='gbp'),
        ],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ])

    return curr_keyboard


@create_session
def user_curr_check(update: Update, context: CallbackContext, db):
    query = update.callback_query
    message = query.message
    query.answer()
    context.user_data['cancel_reply_msg_id'] = message.message_id

    msg = '🆗 Обрано зміну валют.\n\nМенеджемент валютами можеш проводити нижче, щоб відстежувати відповідну.'

    if curr_models := get_curr_by_user_id(db, update.effective_user.id):
        data = [model.name for model in curr_models]
    else:
        data = []

    curr_keyboard = compose_curr_keyboard(data)

    context.user_data['msg_with_markup'] = message.edit_text(text=msg, reply_markup=curr_keyboard)
    context.user_data['curr_data'] = data
    return USER_CURR_CHANGE


@create_session
@send_chat_action(ChatAction.TYPING)
def user_curr_change(update: Update, context: CallbackContext, db):
    query = update.callback_query
    query.answer()
    message = query.message

    user_model = get_user(db, update.effective_user.id)

    user_choice = query.data
    data = context.user_data['curr_data']
    model = get_curr_by_name(db, user_choice)
    if user_choice in data:
        data.remove(user_choice)
        user_model.currency.remove(model)
    else:
        data.extend([user_choice])
        user_model.currency.append(model)

    db.commit()

    curr_keyboard = compose_curr_keyboard(data)
    message.edit_reply_markup(curr_keyboard)

    context.user_data['curr_data'] = data

    return USER_CURR_CHANGE


settings_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings)],
    states={
        CONV_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(user_city_check, pattern='^city$'),
            CallbackQueryHandler(user_timezone_check, pattern='^timezone$'),
            CallbackQueryHandler(user_crypto_check, pattern='^crypto$'),
            CallbackQueryHandler(user_curr_check, pattern='^curr$'),
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
        ],
        USER_CURR_CHANGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(user_curr_change, pattern=r'\w')
        ]
    },
    fallbacks=[
        MessageHandler(Filters.all, cancel)
    ],
    conversation_timeout=300.0
)
