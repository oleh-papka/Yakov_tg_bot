import urllib.parse

import requests

from config import Config
from utils.time_utils import UserTime


class TemperatureFeels:
    def __init__(self, weather_data):
        weather_data_feels = weather_data['daily'][0]['feels_like']

        self.now = str(weather_data['current']['feels_like'])
        self.morn = str(weather_data_feels['morn'])
        self.day = str(weather_data_feels['day'])
        self.eve = str(weather_data_feels['eve'])
        self.night = str(weather_data_feels['night'])


class Temperature:
    def __init__(self, weather_data):
        temp = weather_data['daily'][0]['temp']

        self.min = str(temp['min'])
        self.max = str(temp['max'])
        self.now = str(weather_data['current']['temp'])

        self.feels = TemperatureFeels(weather_data)


def get_sinoptik_url(city_name: str) -> str | None:
    city_name = city_name.replace(' ', '-')
    sinoptik_base_url = f'https://ua.sinoptik.ua/погода-{city_name}'
    response = requests.get(sinoptik_base_url)

    if response.ok:
        return sinoptik_base_url
    else:
        return None


def get_city_info(city_name: str) -> dict | None:
    city_name = city_name.replace(' ', '-')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}' \
          f'&appid={Config.OWM_API_TOKEN}&units=metric&lang=ua'

    data = requests.get(url).json()
    city_data = None

    if data['cod'] == 200:
        city_data = {
            'id': data['id'],
            'name': data['name'],
            'lat': data['coord']['lat'],
            'lon': data['coord']['lon'],
            'timezone_offset': data['timezone']
        }

    return city_data


def get_weather_pic(city_url: str | None = None, date: str | None = None) -> requests.Response | None:
    if city_url is None:
        return None

    if date is None:
        date = ''

    sinoptik_base_url = f'{city_url}/{date}'
    sinoptik_url = urllib.parse.quote(sinoptik_base_url)

    url = f'https://shot.screenshotapi.net/screenshot?token={Config.SCREENSHOT_API_TOKEN}&url={sinoptik_url}&width' \
          f'=1920&height=1080&output=image&file_type=png&block_ads=true&wait_for_event=load&selector=.tabsContentInner'

    resp = requests.get(url)

    if resp.ok:
        return resp
    else:
        return None


def get_weather_data_owm(lat: float, lon: float) -> requests.Response | None:
    url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,' \
          f'alerts&units=metric&appid={Config.OWM_API_TOKEN}'

    response = requests.get(url)
    if response.ok:
        return response
    else:
        return


def get_emoji(weather_cond: str, time: UserTime, sunrise: UserTime, sunset: UserTime):
    emoji = ''

    if weather_cond == 'Thunderstorm':
        emoji = '⛈'
        weather_cond = 'Гроза'
    elif weather_cond == 'Drizzle':
        emoji = '🌨'
        weather_cond = 'Дощик'
    elif weather_cond == 'Rain':
        emoji = '🌧'
        weather_cond = 'Дощ'
    elif weather_cond == 'Snow':
        emoji = '❄'
        weather_cond = 'Сніг'
    elif weather_cond == 'Atmosphere':
        emoji = '🌫'
        weather_cond = 'Туман'
    elif weather_cond == 'Clouds':
        emoji = '☁'
        weather_cond = 'Хмарно'
    elif weather_cond == 'Clear':
        if sunrise < time < sunset:
            emoji = '☀'
            weather_cond = 'Сонячно'
        else:
            emoji = '🌙'
            weather_cond = 'Чисте небо'

    emoji += '️'
    return emoji, weather_cond


def get_weather_text(weather_data, date: None | str = None, city: None | str = None):
    tomorrow_flag = True if date else False
    temp = Temperature(weather_data)
    offset = weather_data['timezone_offset']
    date_n = 1 if tomorrow_flag else 0
    sunrise = UserTime.from_epoch(weather_data['daily'][date_n]['sunrise'])
    sunset = UserTime.from_epoch(weather_data['daily'][date_n]['sunset'])
    wind_speed = weather_data['daily'][date_n]['wind_speed']
    pop = int(float(weather_data['daily'][date_n]['pop']) * 100)
    user_time = UserTime(offset=offset)
    weather_intervals = []
    date_repr = 'завтра' if tomorrow_flag else 'сьогодні'
    output = f'Погода, {city}{date_repr} \({user_time.date_repr(True)}\) :\n\n'

    if tomorrow_flag:
        start_n = 24 - user_time.hour
        end_n = start_n + 25
    else:
        start_n = 0
        end_n = 25 - user_time.hour

    cond_prev = weather_data['hourly'][start_n]['weather'][0]['main']

    for i in range(start_n, end_n):
        time = UserTime.from_epoch(weather_data['hourly'][i]['dt'], offset)
        cond = weather_data['hourly'][i]['weather'][0]['main']

        if cond == cond_prev:
            if len(weather_intervals) == 0:
                weather_intervals.append({'cond': cond, 'start': time})
            else:
                weather_intervals[-1]['end'] = time

            cond_prev = cond
        else:
            weather_intervals.append({'cond': cond, 'start': time})
            cond_prev = cond

    if len(weather_intervals) == 1 or True:
        emoji, weather = get_emoji(weather_intervals[0]['cond'],
                                   weather_intervals[0]['start'],
                                   sunrise,
                                   sunset)
        output += f'{emoji} {weather} весь час\n'
    else:
        for interval in weather_intervals:
            cond = interval['cond']
            start = interval['start']
            end = interval.get('end')
            emoji, weather = get_emoji(cond, start, sunrise, sunset)

            if end:
                output += f'{emoji} {weather}: {start.time_repr()}-{end.time_repr()}\n'
            else:
                output += f'{emoji} {weather} {start.time_repr()}\n'

    output += '\n'

    output += f'🌡️ Температура: \(зараз {temp.now}℃\)\n'
    output += f'{Config.SPACING}мін: {temp.min}℃\n' \
              f'{Config.SPACING}макс: {temp.max}℃\n\n'
    output += f'😶 Відчувається: \(зараз {temp.feels.now}℃\)\n'

    if user_time.hour <= 10:
        output += f'{Config.SPACING}ранок: {temp.feels.morn}℃\n'
    if user_time.hour <= 16:
        output += f'{Config.SPACING}день: {temp.feels.day}℃\n'
    if user_time.hour <= 20:
        output += f'{Config.SPACING}день: {temp.feels.day}℃\n' \
                  f'{Config.SPACING}ніч: {temp.feels.night}℃\n\n'

    output += f'🌀 Швидкість вітру: {wind_speed}м/с\n'
    output += f'💧 Ймовірність опадів: {pop}%\n\n'
    output += f'🌅 Схід: {sunrise.time_repr()},  🌆 Захід: {sunset.time_repr()}'

    return output
