import json

import requests
from bs4 import BeautifulSoup
from sqlalchemy import Result

from config import Config
from models.errors import Privat24APIError, MinFinFetchError, MinFinParseError


def compose_currencies_msg(ccy_data: dict, ccy_models: Result) -> str:
    msg = ""

    for model in ccy_models:
        name = model.name.upper()
        emoji = model.symbol
        ccy = ccy_data[name]
        nb_text = str()
        msg += f"{emoji} *{name.upper()}*\n"

        for market_type, price in ccy.items():
            if len(price) == 2:
                if market_type == 'ПриватБанк':
                    msg += '\n'

                msg += f"{Config.SPACING}{market_type}:  {price[0]:,.2f} | {price[1]:,.2f}\n"

                if market_type == 'Privat24':
                    msg += '\n'
            else:
                nb_text = f"{Config.SPACING}{market_type}:  {price[0]:,.2f}\n"

        msg += f"{nb_text}\n"

    return msg


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


class MinFinScrapper:
    base_url = 'https://minfin.com.ua/ua/{}'

    @staticmethod
    def get_currencies_prices():
        endpoint_url = 'currency/'
        request_url = MinFinScrapper.base_url.format(endpoint_url)

        response = requests.get(request_url)
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

            ccy_data[ccy]["Обмінники"] = [cash_buy, cash_sell]

        return ccy_data
