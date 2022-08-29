from telegram import ChatAction, Update, ParseMode, MessageEntity
from telegram.ext import CommandHandler, CallbackContext

from crud.city import get_city_by_user
from crud.user import auto_create_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action, escape_str_md2
from utils.time_utils import UserTime
from utils.weather_utils import get_weather_pic, get_weather_data_owm, get_weather_text


@create_session
@send_chat_action(ChatAction.UPLOAD_PHOTO)
def weather(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    auto_create_user(db, user)

    row = get_city_by_user(db, user.id)
    if not row:
        message.reply_text('⚠ Схоже місто для погоди не налаштовано, без цьго я не знаю, що робити!\n\n'
                           'Для налаштування міста обери відповідний пункт у налаштуваннях - /settings')
        return

    city_model, user_model = row[0], row[1]
    user_time = UserTime(offset=user_model.timezone_offset)
    date = user_time.tomorrow.date_repr() if user_time.next_day_flag else None

    weather_in_msg = f'Погода у {city_model.name}'

    if url := city_model.url:
        took_from_msg = f'{weather_in_msg}, взяв [тут]({url}).'
        if picture := get_weather_pic(url, date):
            message.reply_photo(picture.content,
                                caption=escape_str_md2(took_from_msg, MessageEntity.TEXT_LINK),
                                parse_mode=ParseMode.MARKDOWN_V2)
            return

    message.reply_chat_action(ChatAction.TYPING)
    data = get_weather_data_owm(city_model.lat, city_model.lon).json()

    url = f'https://openweathermap.org/city/{city_model.owm_id}'
    city = f'у [{city_model.name}]({url}) '
    msg = get_weather_text(data, date, city) + '\n\nДля того щоб отримувати картинку замість тексту, напиши назву ' \
                                               'міста українською, для налаштування цього обери відповідний пункт у ' \
                                               'налаштуваннях - /settings '
    message.reply_text(escape_str_md2(msg, MessageEntity.TEXT_LINK), parse_mode=ParseMode.MARKDOWN_V2,
                       disable_web_page_preview=True)


weather_command_handler = CommandHandler('weather', weather)
