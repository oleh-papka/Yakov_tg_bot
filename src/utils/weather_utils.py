from urllib.parse import quote, unquote

import requests

from src.config import Config
from src.models import City
from src.models.errors import CityFetchError, WeatherFetchError, SinoptikURLFetchError, ScreenshotAPIError
from src.utils.time_utils import UserTime


class TemperatureFeels:
    def __init__(self, weather_data: dict) -> None:
        weather_data_feels = weather_data['daily'][0]['feels_like']

        self.now = str(weather_data['current']['feels_like'])
        self.morn = str(weather_data_feels['morn'])
        self.day = str(weather_data_feels['day'])
        self.eve = str(weather_data_feels['eve'])
        self.night = str(weather_data_feels['night'])


class Temperature:
    def __init__(self, weather_data: dict) -> None:
        temp = weather_data['daily'][0]['temp']

        self.min = str(temp['min'])
        self.max = str(temp['max'])
        self.now = str(weather_data['current']['temp'])

        self.feels = TemperatureFeels(weather_data)


class OpenWeatherMapAPI:
    @staticmethod
    def get_city(city_name: str) -> dict:
        """Fetch city id, english name, coords, local_names, timezone"""
        city_name = city_name.replace(' ', '-')
        geo_url = (f'http://api.openweathermap.org/geo/1.0/direct?'
                   f'q={city_name}&appid={Config.OWM_API_TOKEN}')
        geo_resp = requests.get(geo_url)

        city_data = {}

        if geo_resp.ok:
            try:
                geo_data = geo_resp.json()[0]
            except:
                raise CityFetchError(f'Cannot fetch general info data about city: "{city_name}"')

            local_names = geo_data.get('local_names')
            if not local_names:
                raise CityFetchError(f'Cannot fetch general info data about city: "{city_name}"')

            local_name = local_names.get('uk') or local_names.get('ru')

            city_data |= {
                'name': geo_data.get('name'),
                'local_name': unquote(local_name),
                'lat': geo_data.get('lat'),
                'lon': geo_data.get('lon')
            }
        else:
            raise CityFetchError(f'Cannot fetch geo data about city: "{city_name}"')

        # Get city id, timezone
        weather_url = (
            f'https://api.openweathermap.org/data/2.5/weather?'
            f'q={city_name}&appid={Config.OWM_API_TOKEN}&units=metric&lang=ua'
        )
        weather_resp = requests.get(weather_url)

        if weather_resp.ok:
            weather_data = weather_resp.json()
            city_data |= {
                'id': weather_data['id'],
                'timezone_offset': weather_data['timezone']
            }
        else:
            raise CityFetchError(f'Cannot fetch general info data about city: "{city_name}"')

        return city_data

    @staticmethod
    def get_weather(lat: float, lon: float) -> dict:
        """Fetch all weather data about city by coordinates"""
        url = (
            f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&'
            f'lon={lon}&exclude=minutely,alerts&units=metric&'
            f'appid={Config.OWM_API_TOKEN}'
        )
        resp = requests.get(url)

        if resp.ok:
            return resp.json()
        else:
            raise WeatherFetchError(f'Cannot fetch weather data about city  with coordinates: "{lat}", "{lon}"')

    @staticmethod
    def compose_msg(city_model: City, user_time: UserTime) -> str:
        weather_data = OpenWeatherMapAPI.get_weather(city_model.lat, city_model.lon)

        temp = Temperature(weather_data)
        offset = weather_data['timezone_offset']

        if user_time.next_day_flag:
            date_verbose = 'завтра'
            date_n = 1
            start_n = 24 - user_time.hour
            end_n = start_n + 25
        else:
            date_verbose = 'сьогодні'
            date_n = 0
            start_n = 0
            end_n = 25 - user_time.hour

        url = f'https://openweathermap.org/city/{city_model.owm_id}'
        output = (f'Погода {city_model.local_name} {date_verbose} '
                  f'\\({user_time.date_repr(True)}\\), взяв [тут]({url}):\n\n')

        sunrise = UserTime.from_epoch(weather_data['daily'][date_n]['sunrise'])
        sunset = UserTime.from_epoch(weather_data['daily'][date_n]['sunset'])
        wind_speed = weather_data['daily'][date_n]['wind_speed']
        pop = int(float(weather_data['daily'][date_n]['pop']) * 100)

        weather_intervals = []
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
                    output += (f'{emoji} {weather}: '
                               f'{start.time_repr()}-{end.time_repr()}\n')
                else:
                    output += f'{emoji} {weather} {start.time_repr()}\n'

        output += f'\n🌡️ Температура: \\(зараз {temp.now}℃\\)\n'
        output += (f'{Config.SPACING}мін: {temp.min}℃\n'
                   f'{Config.SPACING}макс: {temp.max}℃\n\n')
        output += f'😶 Відчувається: \\(зараз {temp.feels.now}℃\\)\n'

        if user_time.hour <= 10:
            output += f'{Config.SPACING}ранок: {temp.feels.morn}℃\n'
        if user_time.hour <= 16:
            output += f'{Config.SPACING}день: {temp.feels.day}℃\n'
        if user_time.hour <= 20:
            output += (f'{Config.SPACING}день: {temp.feels.day}℃\n'
                       f'{Config.SPACING}ніч: {temp.feels.night}℃\n\n')

        output += f'🌀 Швидкість вітру: {wind_speed}м/с\n'
        output += f'💧 Ймовірність опадів: {pop}%\n\n'
        output += (f'🌅 Схід: {sunrise.time_repr()}, '
                   f'🌆 Захід: {sunset.time_repr()}')

        output += (f'\n\n\nP.S. Для того, щоб отримувати картинку замість тексту, потрібні грошики💸, тому її немає.\n\n'
                   f'P.P.S. Проте можеш поглянути на картинку [тут]({city_model.sinoptik_url}).')

        return output


class SinoptikScraper:
    @staticmethod
    def get_url(city_name: str) -> str:
        city_name = city_name.replace(' ', '-')
        base_url = f'https://ua.sinoptik.ua/погода-{city_name}'
        resp = requests.get(base_url)

        if resp.ok:
            return base_url
        else:
            raise SinoptikURLFetchError


class ScreenshotAPI:
    @staticmethod
    def get_photo(sinoptik_url: str, date: str | None = None) -> requests.Response:
        if date is not None:
            sinoptik_url = f'{sinoptik_url}/{date}'

        sinoptik_url = quote(sinoptik_url)

        url = (f'https://shot.screenshotapi.net/screenshot?token='
               f'{Config.SCREENSHOT_API_TOKEN}&url={sinoptik_url}&width=1920'
               f'&height=1080&output=image&file_type=png&block_ads=true&'
               f'wait_for_event=load&selector=.tabsContentInner')

        resp = requests.get(url)

        if resp.ok:
            return resp
        else:
            raise ScreenshotAPIError(f'Cannot get screenshot for city with url: "{sinoptik_url}"')


def get_emoji(weather_cond: str,
              time: UserTime,
              sunrise: UserTime,
              sunset: UserTime):
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
