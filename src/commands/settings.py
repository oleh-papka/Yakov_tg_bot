import re

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, \
    filters

from src.config import Config
from src.crud.city import create_city, get_city_by_name
from src.crud.crypto_currency import get_crypto_by_user_id, get_crypto_by_abbr
from src.crud.currency import get_curr_by_user_id, get_curr_by_name
from src.crud.user import create_or_update_user, get_user_by_id, update_user
from src.handlers.canel_conversation import cancel, cancel_back_keyboard
from src.models.errors import CityFetchError
from src.utils.db_utils import get_session
from src.utils.message_utils import send_typing_action
from src.utils.time_utils import UserTime
from src.utils.weather_utils import OpenWeatherMapAPI, SinoptikScraper

SETTINGS_START, CITY_SETTINGS, TIMEZONE_SETTINGS, CRYPTO_SETTINGS, CURR_SETTINGS = 1, 2, 3, 4, 5

main_settings_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton('Місто 🏙️', callback_data='city_settings')],
    [InlineKeyboardButton('Часовий пояс 🌐', callback_data='timezone_settings')],
    [InlineKeyboardButton('Крипто валюти 🪙', callback_data='crypto_settings')],
    [InlineKeyboardButton('Фіатні валюти 🇺🇦', callback_data='curr_settings')],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
], )


@send_typing_action
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = message.from_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    settings_start_text = 'Бажаєш налаштувати щось?\nОбери з нижче наведених опцій:'

    context.user_data['markup_msg'] = await message.reply_text(settings_start_text, reply_markup=main_settings_keyboard)

    return SETTINGS_START


async def back_to_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    settings_start_text = 'Шукаєш щось інше?\nОбери з нижче наведених опцій:'

    await query.edit_message_text(text=settings_start_text, reply_markup=main_settings_keyboard)

    return SETTINGS_START


async def city_settings_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = update.effective_user
    message = query.message
    await query.answer()

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        users_city_model = user_model.city

    if users_city_model:
        city_change_text = (f'⚠ В тебе уже вказане місто - {users_city_model.local_name}. '
                            f'Ти справді хочеш його змінити?\n\nДля зміни надішли назву міста або пряме '
                            f'посилання на нього з ua.sinoptik.ua у наступному повідомленні.')
    else:
        city_change_text = ('🆗 Обрано зміну міста для прогнозу погоди.\n\n'
                            'Надішли мені назву міста або пряме посилання на нього з ua.sinoptik.ua '
                            'у наступному повідомленні, щоб встановити відповідне.')

    context.user_data['markup_msg'] = await message.edit_text(text=city_change_text, reply_markup=cancel_back_keyboard)

    return CITY_SETTINGS


@send_typing_action
async def city_settings_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']

    await markup_msg.edit_reply_markup(reply_markup=None)
    user_input = message.text.strip()

    try:
        if url := SinoptikScraper.check_url(user_input):
            city_name = re.sub(r'https://ua.sinoptik.ua/погода-', '', url)
            city_name_no_digits = re.sub(r'-\d+', '', city_name)
            city_data = OpenWeatherMapAPI.get_city(city_name_no_digits)
        else:
            city_data = OpenWeatherMapAPI.get_city(user_input)
    except CityFetchError:
        city_not_found_text = ('⚠ Cхоже назва міста вказана не вірно(або я дурний), бо не можу знайти такого міста.'
                               '\n\nСпробуй ще раз нижче')

        context.user_data['markup_msg'] = await message.reply_text(city_not_found_text,
                                                                   reply_markup=cancel_back_keyboard,
                                                                   quote=True)
        return CITY_SETTINGS

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        users_city_model = user_model.city

    city_name_local = city_data['local_name']
    city_name_eng = city_data['name']
    city_change_text = f'✅ Зроблено, твоє місто тепер - {city_name_local}.\n\nЩось ще?'

    if users_city_model and users_city_model.name == city_name_eng:
        city_change_text = '❕ Так це ж те саме місто, жодних змін не вношу 🙃\n\nЩось ще?'

        await message.reply_text(city_change_text, reply_markup=main_settings_keyboard)
        return SETTINGS_START

    sinoptik_base_url = url if url else SinoptikScraper.get_url(city_name_local)
    city_timezone_offset = city_data['timezone_offset']

    async with get_session() as session:
        city_model = await get_city_by_name(session, city_name_eng)
        if not city_model:
            await create_city(session,
                              owm_id=city_data['id'],
                              name=city_name_eng,
                              local_name=city_name_local,
                              lat=city_data['lat'],
                              lon=city_data['lon'],
                              sinoptik_url=sinoptik_base_url,
                              timezone_offset=city_timezone_offset)

        city_model = await get_city_by_name(session, city_name_eng)

        await update_user(session, user, {'city_id': city_model.id})

    city_changed_message = await message.reply_text(city_change_text,
                                                    reply_to_message_id=message.message_id,
                                                    reply_markup=main_settings_keyboard)

    if city_timezone_offset and (city_timezone_offset != user_model.timezone_offset):
        city_change_text = city_change_text.replace('\n\nЩось ще?', '')
        city_change_text += '\n\n❕ У тебе і цього міста різні часові пояси, змінити на відповідний місту часовий пояс?'
        approve_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f'Змінити на "{UserTime.offset_repr(city_timezone_offset)}"',
                                  callback_data='change_to_city')],
            [InlineKeyboardButton('Детальні налаштування 🌐', callback_data='timezone_settings')],
            [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
        ])

        context.user_data['markup_msg'] = await city_changed_message.edit_text(city_change_text,
                                                                               reply_markup=approve_keyboard)
        return TIMEZONE_SETTINGS

    command_msg = context.user_data.get('command_msg')
    context.user_data.clear()
    context.user_data['command_msg'] = command_msg
    context.user_data['markup_msg'] = city_changed_message

    return SETTINGS_START


async def change_timezone_to_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = update.effective_user
    await query.answer()

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        users_city_model = user_model.city
        timezone_offset = users_city_model.timezone_offset
        city_name = users_city_model.local_name
        await update_user(session, user, {'timezone_offset': timezone_offset})

    timezone_changed_text = (f'✅ Зроблено, твій часовий пояс тепер відповідає вказаному місту '
                             f'{city_name} ({UserTime.offset_repr(timezone_offset)}).'
                             f'\n\n Щось ще?')
    await query.edit_message_text(text=timezone_changed_text, reply_markup=main_settings_keyboard)

    command_msg = context.user_data.get('command_msg')
    markup_msg = context.user_data.get('markup_msg')
    context.user_data.clear()
    context.user_data['command_msg'] = command_msg
    context.user_data['markup_msg'] = markup_msg

    return SETTINGS_START


async def timezone_settings_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']

    await query.answer()
    if markup_msg:
        await markup_msg.edit_reply_markup(reply_markup=None)

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        users_city_model = user_model.city

    timezone_change_text = ('🆗 Обрано зміну часового поясу.\n\n'
                            'Поточні дані часового поясу:\n')
    if users_city_model:
        timezone_change_text += (f'{Config.SPACING}У місті {users_city_model.local_name}: '
                                 f'{UserTime.offset_repr(users_city_model.timezone_offset)}\n')

    timezone_change_text += (f'{Config.SPACING}Вказаний в профілі: '
                             f'{UserTime.offset_repr(user_model.timezone_offset)}\n\n'
                             f'Для зміни часового поясу надішли відповідний у наступному повідомленні (Приклад: +3).')

    await message.edit_text(text=timezone_change_text, reply_markup=cancel_back_keyboard)

    return TIMEZONE_SETTINGS


@send_typing_action
async def user_timezone_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']

    await markup_msg.edit_reply_markup(reply_markup=None)
    user_input = message.text.strip()

    if re.match(r'^[+|-]?[1-9][0-2]?$', user_input) and abs(int(user_input)) in range(1, 13):
        timezone_offset = int(user_input) * 3600
    else:
        timezone_change_error_text = '⚠ Cхоже часовий пояс вказано не вірно, спробуй ще раз.'
        context.user_data['markup_msg'] = await message.reply_text(text=timezone_change_error_text,
                                                                   reply_markup=cancel_back_keyboard)
        return TIMEZONE_SETTINGS

    async with get_session() as session:
        await update_user(session, user, {'timezone_offset': timezone_offset})

    timezone_change_text = (f'✅ Зроблено, твій часовий пояс тепер {UserTime.offset_repr(timezone_offset)}'
                            f'\n\nЩось ще?')
    markup_msg = await message.reply_text(text=timezone_change_text, reply_markup=main_settings_keyboard)

    command_msg = context.user_data.get('command_msg')
    context.user_data.clear()
    context.user_data['command_msg'] = command_msg
    context.user_data['markup_msg'] = markup_msg

    return SETTINGS_START


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
        [InlineKeyboardButton('🔙 Назад', callback_data='back')],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ])

    return crypto_keyboard


async def crypto_settings_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = update.effective_user
    message = query.message
    context.user_data['markup_msg'] = message.message_id

    await query.answer()

    crypto_change_text = ('🆗 Обрано зміну криптовалют.\n\nМенеджемент криптою можеш проводити нижче,'
                          ' щоб відстежувати відповідну.')

    async with get_session() as session:
        if crypto_models := await get_crypto_by_user_id(session, user.id):
            data = [model.abbr for model in crypto_models]
        else:
            data = []

    crypto_keyboard = compose_crypto_keyboard(data)

    context.user_data['markup_msg'] = await message.edit_text(text=crypto_change_text, reply_markup=crypto_keyboard)
    context.user_data['crypto_data'] = data

    return CRYPTO_SETTINGS


async def user_crypto_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    user = update.effective_user
    user_choice = query.data
    data = context.user_data['crypto_data']

    await query.answer()
    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        model = await get_crypto_by_abbr(session, user_choice)

        if user_choice in data:
            data.remove(user_choice)
            user_model.crypto_currency.remove(model)
        else:
            data.extend([user_choice])
            user_model.crypto_currency.append(model)

        await session.commit()

    crypto_keyboard = compose_crypto_keyboard(data)
    await message.edit_reply_markup(crypto_keyboard)

    context.user_data['crypto_data'] = data

    return CRYPTO_SETTINGS


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
        [InlineKeyboardButton('🔙 Назад', callback_data='back')],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ])

    return curr_keyboard


async def curr_settings_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = update.effective_user
    message = query.message
    context.user_data['markup_msg'] = message.message_id

    await query.answer()

    curr_change_text = ('🆗 Обрано зміну валют.\n\nМенеджемент валютами можеш проводити нижче, '
                        'щоб відстежувати відповідну.')

    async with get_session() as session:
        if curr_models := await get_curr_by_user_id(session, user.id):
            data = [model.name for model in curr_models]
        else:
            data = []

    curr_keyboard = compose_curr_keyboard(data)

    context.user_data['markup_msg'] = await message.edit_text(text=curr_change_text, reply_markup=curr_keyboard)
    context.user_data['curr_data'] = data

    return CURR_SETTINGS


async def user_curr_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    user = update.effective_user
    user_choice = query.data
    data = context.user_data['curr_data']

    await query.answer()
    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        model = await get_curr_by_name(session, user_choice)

        if user_choice in data:
            data.remove(user_choice)
            user_model.currency.remove(model)
        else:
            data.extend([user_choice])
            user_model.currency.append(model)

        await session.commit()

    curr_keyboard = compose_curr_keyboard(data)
    await message.edit_reply_markup(curr_keyboard)

    context.user_data['curr_data'] = data

    return CURR_SETTINGS


settings_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings)],
    states={
        SETTINGS_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(city_settings_start, pattern='^city_settings$'),
            CallbackQueryHandler(timezone_settings_start, pattern='^timezone_settings$'),
            CallbackQueryHandler(crypto_settings_start, pattern='^crypto_settings$'),
            CallbackQueryHandler(curr_settings_start, pattern='^curr_settings$')
        ],
        CITY_SETTINGS: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_settings, pattern='^back$'),
            MessageHandler(filters.TEXT, city_settings_change)
        ],
        TIMEZONE_SETTINGS: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_settings, pattern='^back$'),
            CallbackQueryHandler(change_timezone_to_city, pattern='^change_to_city$'),
            CallbackQueryHandler(timezone_settings_start, pattern='^timezone_settings$'),
            MessageHandler(filters.TEXT, user_timezone_change)
        ],
        CRYPTO_SETTINGS: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_settings, pattern='^back$'),
            CallbackQueryHandler(user_crypto_change, pattern=r'\w')
        ],
        CURR_SETTINGS: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_settings, pattern='^back$'),
            CallbackQueryHandler(user_curr_change, pattern=r'\w')
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL & filters.COMMAND, cancel)
    ],
    conversation_timeout=300.0
)
