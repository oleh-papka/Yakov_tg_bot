import json
from datetime import datetime, time, timedelta

import requests
from telegram import ChatAction, Update
from telegram.ext import CommandHandler, CallbackContext

from config import Config
from utils import get_user_time


def get_weather_pic(date: str | None = None) -> requests.Response | None:
    if date is None:
        date = ''
    else:
        date = '/' + date

    query = f'https://shot.screenshotapi.net/screenshot?token={Config.SCREENSHOT_API_TOKEN}&url=https%3A%2F%2Fua' \
            f'.sinoptik.ua%2F%25D0%25BF%25D0%25BE%25D0%25B3%25D0%25BE%25D0%25B4%25D0%25B0-%25D1%2582%25D0%25B5%25D1' \
            f'%2580%25D0%25BD%25D0%25BE%25D0%25BF%25D1%2596%25D0%25BB%25D1%258C' \
            f'{date}&width=1920&height=1080&output=image&file_type=png&block_ads=true&wait_for_event=load&selector' \
            f'=.tabsContentInner '

    resp = requests.get(query)

    if resp.ok:
        return resp
    else:
        return None


def formatted_time(time_unix: int, time_offset: int) -> str:
    return datetime.utcfromtimestamp(time_unix + time_offset).strftime('%H:%M')


def get_emoji(weather_cond: str, time_unix: time, sunrise_unix: time, sunset_unix: time, flag_tomorrow: bool = False):
    emoji = ''

    if weather_cond == 'Thunderstorm':
        emoji = '⛈️'
        weather_cond = 'Гроза'
    elif weather_cond == 'Drizzle':
        emoji = '🌧️'
        weather_cond = 'Дощик'
    elif weather_cond == 'Rain':
        emoji = '🌧️'
        weather_cond = 'Дощ'
    elif weather_cond == 'Snow':
        emoji = '❄️'
        weather_cond = 'Сніг'
    elif weather_cond == 'Atmosphere':
        emoji = '🌫️'
        weather_cond = 'Туман'
    elif weather_cond == 'Clouds':
        emoji = '☁️'
        weather_cond = 'Хмарно'
    elif weather_cond == 'Clear':
        if sunrise_unix < time_unix < sunset_unix or flag_tomorrow:
            emoji = '☀️'
            weather_cond = 'Сонячно'
        else:
            emoji = '🌒'
            weather_cond = 'Чисте небо'

    return emoji, weather_cond


def get_weather_details(curr_time: datetime, lat: float = 49.5559, lon: float = 25.6056) -> str:
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,' \
          f'alerts&units=metric&appid={Config.OWM_API_TOKEN}'

    data = requests.get(url).json()

    time_offset_unix = data['timezone_offset']
    time_sunrise_unix = data['current']['sunrise']
    time_sunset_unix = data['current']['sunset']

    time_sunrise = formatted_time(time_sunrise_unix, time_offset_unix)
    time_sunset = formatted_time(time_sunset_unix, time_offset_unix)

    temp_min = str(data['daily'][0]['temp']['min'])
    temp_max = str(data['daily'][0]['temp']['max'])
    temp_now = str(data['current']['temp'])
    temp_now_feels = str(data['current']['feels_like'])
    temp_morn_feels = str(data['daily'][0]['feels_like']['morn'])
    temp_day_feels = str(data['daily'][0]['feels_like']['day'])
    temp_eve_feels = str(data['daily'][0]['feels_like']['eve'])
    temp_night_feels = str(data['daily'][0]['feels_like']['night'])
    wind_speed_now = str(data['current']['wind_speed'])
    pop_now = str(int(float(data['daily'][0]['pop']) * 100))

    output = 'Погода сьогодні:\n\n'

    counter = 0
    midnight_flag = False

    weather_time = data['hourly'][counter]['dt']

    temp_intervals = []
    res_intervals = []

    if formatted_time(weather_time, time_offset_unix) == '00:00':
        counter = 1
        midnight_flag = True

    weather_time = data['hourly'][counter]['dt']

    while formatted_time(weather_time, time_offset_unix) != '00:00':
        weather_time = data['hourly'][counter]['dt']
        weather_text = data['hourly'][counter]['weather'][0]['main']

        if counter == 0 or midnight_flag is True:
            midnight_flag = False
            temp_intervals.append(weather_text)
            temp_intervals.append(weather_time)
        else:
            weather_previous = data['hourly'][counter - 1]['weather'][0]['main']
            if weather_previous == weather_text:
                temp_intervals.append(weather_time)
            else:
                res_intervals.append(temp_intervals)
                temp_intervals = [weather_text, weather_time]

        counter += 1

        if formatted_time(weather_time, time_offset_unix) == '00:00':
            res_intervals.append(temp_intervals)

    for interval in res_intervals:
        if len(interval) >= 3:
            emoji, wthr = get_emoji(interval[0], interval[1], time_sunrise_unix, time_sunset_unix)
            s_t = formatted_time(interval[1], time_offset_unix)
            e_t = formatted_time(interval[-1], time_offset_unix)
            output += f'{emoji} {wthr}: {s_t}-{e_t}\n'
        else:
            emoji, wthr = get_emoji(interval[0], interval[-1], time_sunrise_unix, time_sunset_unix)
            t = formatted_time(interval[-1], time_offset_unix)
            output += f'{emoji} {wthr} {t}\n'

        output += '\n'

        output += f'🌡️ Температура: (зараз {temp_now}℃)\n'
        output += f'⠀⠀ мін: {temp_min}℃\n⠀⠀ макс: {temp_max}℃\n\n'
        output += f'😶 Відчувається: (зараз {temp_now_feels}℃)\n'

        time_interval = int(curr_time.hour)

        if 5 < time_interval <= 10:
            output += f'⠀⠀ ранок: {temp_morn_feels}℃\n⠀⠀ день: {temp_day_feels}℃\n⠀⠀ вечір: {temp_eve_feels}℃\n\n'
        elif 10 < time_interval <= 16:
            output += f'⠀⠀ день: {temp_day_feels}℃\n⠀⠀ вечір: {temp_eve_feels}℃\n\n'
        elif 16 < time_interval < 21:
            output += f'⠀⠀ вечір: {temp_eve_feels}℃\n\n⠀⠀ ніч: {temp_night_feels}℃\n\n'
        else:
            output += f'⠀⠀ ніч: {temp_night_feels}℃\n\n'

        output += f'🌀 Швидкість вітру: {wind_speed_now}м/с\n'
        output += f'💧 Ймовірність опадів: {pop_now}%\n\n'
        output += f'🌅 Схід: {time_sunrise},  🌆 Захід: {time_sunset}'

        return output


def get_weather_tomorrow(lat: float = 49.5559, lon: float = 25.6056) -> str:
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,' \
          f'alerts&units=metric&appid={Config.OWM_API_TOKEN}'

    response = requests.get(url)
    data = json.loads(response.text)

    with open('l.json', 'w') as f:
        f.write(json.dumps(data))

    weather_cond = str(data['daily'][1]['weather'][0]['main'])

    time_offset_unix = data['timezone_offset']
    time_sunrise_unix = data['daily'][1]['sunrise']
    time_sunset_unix = data['daily'][1]['sunset']

    emoji, wthr = get_emoji(weather_cond, time(),
                            time_sunrise_unix, time_sunset_unix, flag_tomorrow=True)

    time_sunrise = formatted_time(time_sunrise_unix, time_offset_unix)
    time_sunset = formatted_time(time_sunset_unix, time_offset_unix)

    temp_min = str(data['daily'][1]['temp']['min'])
    temp_max = str(data['daily'][1]['temp']['max'])
    temp_morn_feels = str(data['daily'][1]['feels_like']['morn'])
    temp_day_feels = str(data['daily'][1]['feels_like']['day'])
    temp_eve_feels = str(data['daily'][1]['feels_like']['eve'])
    wind_speed_tomorrow = str(data['daily'][1]['wind_speed'])
    pop_tomorrow = str(int(float(data['daily'][1]['pop']) * 100))

    output = f'Погода на завтра:\n\n{emoji} {wthr}\n\n'
    output += f'🌡️ Температура:\n' \
              f'⠀⠀ мін: {temp_min}℃\n⠀⠀ макс: {temp_max}℃\n\n'
    output += f'😶 Відчувається:\n' \
              f'⠀⠀ ранок: {temp_morn_feels}℃\n⠀⠀ день: {temp_day_feels}℃\n⠀⠀ вечір: {temp_eve_feels}℃\n\n'
    output += f'🌀 Швидкість вітру: {wind_speed_tomorrow}m/s\n'
    output += f'💧 Ймовірність опадів: {pop_tomorrow}%\n\n'
    output += f'🌅 Схід: {time_sunrise},  🌆 Захід: {time_sunset}'

    return output


def weather(update: Update, context: CallbackContext) -> None:
    message = update.message

    message.reply_chat_action(ChatAction.TYPING)
    tmp_msg = message.reply_text('Потрібно зачекати, зараз усе буде)')
    message.reply_chat_action(ChatAction.UPLOAD_PHOTO)

    user_time = get_user_time()['timestamp']

    if int(user_time.hour) in range(20, 24):
        tomorrow = user_time + timedelta(days=1)
        tomorrow = tomorrow.strftime('%Y-%m-%d')

        message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        if resp := get_weather_pic(tomorrow):
            message.reply_photo(resp.content)
        else:
            message.reply_chat_action(ChatAction.TYPING)
            message.reply_text(get_weather_tomorrow())
    else:
        message.reply_chat_action(ChatAction.UPLOAD_PHOTO)
        if resp := get_weather_pic():
            message.reply_photo(resp.content)
        else:
            message.reply_chat_action(ChatAction.TYPING)
            message.reply_text(get_weather_details(curr_time=user_time))

    tmp_msg.delete()


weather_command_handler = CommandHandler('weather', weather)
