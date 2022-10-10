from sqlalchemy.orm import Session
from telegram import ChatAction, Update, ParseMode, MessageEntity
from telegram.ext import CommandHandler, CallbackContext

from crud.city import get_city_by_user
from crud.user import manage_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action, escape_str_md2
from utils.time_utils import UserTime
from utils.weather_utils import ScreenshotAPI, OpenWeatherMapAPI


@create_session
@send_chat_action(ChatAction.UPLOAD_PHOTO)
def weather(update: Update,
            context: CallbackContext,
            db: Session) -> None:
    message = update.message
    user = update.effective_user
    manage_user(db, user)
    row = get_city_by_user(db, user.id)

    if not row:
        message.reply_text(
            '⚠ Схоже місто для погоди не налаштовано, без цьго я не знаю, '
            'що робити!\n\nДля налаштування міста обери відповідний пункт '
            'у налаштуваннях - /settings')
        return

    city_model, user_model = row[0], row[1]
    user_time = UserTime(offset=user_model.timezone_offset)

    if user_time.next_day_flag:
        date = user_time.tomorrow.date_repr()
    else:
        date = user_time.date_repr()

    if sinoptik_url := city_model.sinoptik_url:
        if picture := ScreenshotAPI.get_photo(sinoptik_url, date):
            date_verbose = 'завтра' if user_time.next_day_flag else 'сьогодні'

            took_from_msg = (
                f'Погода {city_model.local_name} {date_verbose} \\('
                f'{user_time.date_repr(True)}\\), взяв [тут]({sinoptik_url}).'
            )
            caption = escape_str_md2(took_from_msg, MessageEntity.TEXT_LINK)

            message.reply_photo(picture.content,
                                caption=caption,
                                parse_mode=ParseMode.MARKDOWN_V2)
            return

    message.reply_chat_action(ChatAction.TYPING)

    user_time = UserTime(offset=user_model.timezone_offset)
    msg = OpenWeatherMapAPI.compose_msg(city_model, user_time)
    # TODO: add question: wanna try to add manually your link?
    msg += ('\n\nДля того щоб отримувати картинку замість тексту, напиши назву'
            ' потрібного міста, для налаштування цього обери відповідний пункт'
            ' у налаштуваннях - /settings')

    message.reply_text(escape_str_md2(msg, MessageEntity.TEXT_LINK),
                       parse_mode=ParseMode.MARKDOWN_V2,
                       disable_web_page_preview=True)


weather_command_handler = CommandHandler('weather', weather)
