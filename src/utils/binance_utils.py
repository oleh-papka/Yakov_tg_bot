import logging
import math

from binance.client import Client

from config import Config
from models.errors import BinanceAPIError
from utils.currency_utils import MinFinScrapper

logger = logging.getLogger(__name__)


def round_down(num: float, digits: int = None):
    if num == 0:
        return 0

    if digits:
        factor = 10 ** digits
    else:
        factor = 10 ** (-math.floor(math.log10(abs(num))))

    return math.floor(num * factor) * (1 / factor)


def compose_binance_msg(funding_wallet_data: list) -> str:
    msg = '\n💸 Binance гаманець:\n'
    sum_price_usdt = 0

    for coin in funding_wallet_data:
        coin_free = float(coin['free'])

        if coin_free > 1:
            coin_free = round_down(coin_free, 2)
        else:
            coin_free = round_down(coin_free)

        usdt_price = coin['price'].get('usdt')

        if coin['asset'] == 'USDT':
            msg += f"{Config.SPACING}`{coin['asset']} {coin_free:,}`\n"
        else:
            msg += f"{Config.SPACING}*{coin['asset']}* {coin_free:,} *|* `USDT {usdt_price:,.2f}`\n"

        sum_price_usdt += usdt_price

    usd_price = MinFinScrapper.get_currencies_prices()['USD']['НБУ'][0]
    msg += f'\nСума: `USDT {sum_price_usdt:,.2f}` | `UAH {sum_price_usdt * usd_price:,.2f}`'

    return msg


class BinanceAPI:
    client = Client(Config.BINANCE_API_TOKEN, Config.BINANCE_API_PRIVAT_TOKEN)

    def get_funding_wallet(self) -> list | None:
        """Fetches Funding wallet data from Binance account

        [{
            "asset": "",
            "free": "",
            "locked": "",
            "freeze": "",
            "withdrawing": "",
            "btcValuation": ""
        }]
        """

        try:
            funding_wallet_data = self.client.funding_wallet()

            if not funding_wallet_data:
                raise BinanceAPIError
        except BinanceAPIError as e:
            logger.error(f"Binance API error! - {e}")
            raise BinanceAPIError(e)

        btc2usdt = float(self.client.get_symbol_ticker(symbol=f"BTCUSDT").get('price'))

        wallet_data = []

        for coin in funding_wallet_data:
            if coin['asset'] == 'ETHW':
                continue

            if coin['asset'] == 'USDT':
                coin2usdt = 1
            else:
                coin2usdt = float(self.client.get_symbol_ticker(symbol=f"{coin['asset']}USDT").get('price'))

                if not coin2usdt:
                    coin2usdt = float(coin['btcValuation']) * btc2usdt

            coin['price'] = {'usdt': coin2usdt * float(coin['free'])}

            wallet_data.append(coin)

        return wallet_data
