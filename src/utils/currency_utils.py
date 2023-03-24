import re

import requests
from bs4 import BeautifulSoup
from sqlalchemy import Result

from src.config import Config
from src.models.errors import Privat24APIError, MinFinFetchError, MinFinParseError
from src.utils.time_utils import UserTime


def get_privat_usd_price() -> dict:
    base_url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid={}"
    market_type_ids = {'ПриватБанк': 5, 'Privat24': 11}
    ccy_data = {}

    for market_type, type_id in market_type_ids.items():
        response = requests.get(base_url.format(type_id))

        if response.ok:
            resp = response.json()
            usd = [ccy for ccy in resp if ccy['ccy'] == "USD"][0]
            ccy_data |= {market_type: [float(usd["buy"]), float(usd["sale"])]}

    if not ccy_data:
        raise Privat24APIError

    return ccy_data


def get_min_fin_price() -> dict:
    # Get html table from MinFin
    all_currencies_url = "https://minfin.com.ua/ua/currency/"

    response = requests.get(all_currencies_url)
    if not response.ok:
        raise MinFinFetchError

    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.select("body > main > div.mfz-container > div > div.mfz-col-content > "
                        "div > section:nth-child(3) > div.mfm-grey-bg > table")
    if not table:
        raise MinFinParseError

    rows = table[0].find_all('tr')[1:]
    if not rows:
        raise MinFinParseError

    # Parse the html table of CCYs
    ccy_data = {}

    for row in rows[:-1]:
        tds = row.find_all('td')
        ccy = tds[0].a.text.strip().upper()
        bank_price = re.sub(r"\n\n[+-]?([0-9]*[.])?[0-9]+ /\n[+-]?([0-9]*[.])?[0-9]+\n\n", ' ',
                            tds[1].text.strip().replace('  ', ' ').replace(',', '.'))
        bank_price = [float(price) for price in bank_price.split()]
        black_market_price = tds[3].text.strip().replace('\n', '').replace('/', '').replace('  ', ' ').replace(',', '.')
        black_market_price = [float(price) for price in black_market_price.split()]
        nb_price = [float(tds[2].text.strip().split()[0])]

        ccy_data[ccy] = {
            "Сер. в банках": bank_price,
            tds[3]['data-title'].strip(): black_market_price,
            tds[2]['data-title'].strip(): nb_price
        }

    return ccy_data


def compose_output(ccy_data: dict, ccy_models: Result) -> str:
    text = ""

    for model in ccy_models:
        name = model.name.upper()
        emoji = model.symbol
        ccy = ccy_data[name]
        nb_text = str()
        text += f"{emoji} *{name.upper()}*\n"

        for market_type, price in ccy.items():
            if len(price) == 2:
                text += f"{Config.SPACING}{market_type}:  _{price[0]:,.2f}₴_ | _{price[1]:,.2f}₴_\n"
            else:
                nb_text = f"{Config.SPACING}{market_type}:  _{price[0]:,.2f}₴_\n"

        text += f"{nb_text}\n"

    return text
