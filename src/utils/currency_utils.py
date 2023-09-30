import json
import re

import requests
from bs4 import BeautifulSoup
from sqlalchemy import Result

from src.config import Config
from src.models.errors import Privat24APIError, MinFinFetchError, MinFinParseError


class Privat24API:
    base_url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid={}"
    market_type_ids = {'ПриватБанк': 5, 'Privat24': 11}

    @staticmethod
    def get_usd_price() -> dict:
        ccy_data = {}

        for market_type, type_id in Privat24API.market_type_ids.items():

            try:
                response = requests.get(Privat24API.base_url.format(type_id))
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise Privat24APIError(f"Privat24API request failed: {e}")

            if response.ok:
                try:
                    resp = response.json()
                except json.JSONDecodeError as e:
                    raise Privat24APIError(f"JSON decoding failed: {e}")

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
    table = soup.select(
        "#root > div > section > div > div > div > main > section.bvp3d3-1.fwOefR > div.bvp3d3-8.bTJUGM > "
        "div:nth-child(1) > div.sc-1x32wa2-0.dWgyGF.bvp3d3-10.kNRLfR > table")
    if not table:
        raise MinFinParseError

    rows = table[0].find_all('tr')[1:]
    if not rows:
        raise MinFinParseError

    ccy_data = {}

    for row in rows[:-1]:
        tds = row.find_all('td')
        ccy = tds[0].a.text.strip().upper()

        bank_buy = float(tds[1].contents[0].next.strip().replace(',', '.'))
        bank_sell = float(tds[2].contents[0].next.strip().replace(',', '.'))

        nb_price = [float(tds[3].contents[0].next.strip().replace(',', '.'))]

        ccy_data[ccy] = {
            "НБУ": nb_price,
            "Сер. банк": [bank_buy, bank_sell],
        }

    table2 = soup.select(
        "#root > div > section > div > div > div > main > section.bvp3d3-1.fwOefR > div.bvp3d3-8.bTJUGM > "
        "div.bvp3d3-9.bvp3d3-12.FqORR.UIaOD > div.sc-1x32wa2-0.dWgyGF.bvp3d3-10.bvp3d3-11.kNRLfR.cLIHts > table")
    if not table2:
        raise MinFinParseError

    rows2 = table[0].find_all('tr')[1:]
    if not rows2:
        raise MinFinParseError

    for row in rows2[:-1]:
        tds = row.find_all('td')
        ccy = tds[0].a.text.strip().upper()

        cash_buy = float(tds[1].contents[0].next.strip().replace(',', '.'))
        cash_sell = float(tds[2].contents[0].next.strip().replace(',', '.'))

        ccy_data[ccy]["Готівка"] = [cash_buy, cash_sell]

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
