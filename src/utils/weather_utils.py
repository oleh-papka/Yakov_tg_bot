import requests

from config import Config


def ping_city_sinoptik(city_name: str) -> str | None:
    city_name = city_name.replace(' ', '-')
    sinoptik_base_url = f'https://ua.sinoptik.ua/погода-{city_name}'
    response = requests.get(sinoptik_base_url)

    if response.ok:
        return sinoptik_base_url
    else:
        return


def ping_city_owm_api(city_name: str) -> dict | None:
    city_name = city_name.replace(' ', '-')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}' \
          f'&appid={Config.OWM_API_TOKEN}&units=metric&lang=ua'

    data = requests.get(url).json()
    city_data = None

    if data['cod'] == 200:
        city_data = {
            'name': data['name'],
            'lat': data['coord']['lat'],
            'lon': data['coord']['lon'],
            'timezone_offset': data['timezone']
        }

    return city_data
