import requests

from src.config import Config


def compose_coins_msg(coins: dict) -> str:
    msg = ''

    for v in coins.values():
        coin_name = v['name']
        coin_abbr = v['symbol']

        price = round(v['quote']['USD']['price'], 1)

        change_1h = round(v['quote']['USD']['percent_change_1h'], 2)
        change_24h = round(v['quote']['USD']['percent_change_24h'], 2)
        change_7d = round(v['quote']['USD']['percent_change_7d'], 2)

        if change_1h > 0.2:
            main_emoji = '💹'
        elif change_1h < -0.2:
            main_emoji = '📉'
        else:
            main_emoji = '📊'

        if change_24h > 3.5 or change_1h > 2.0:
            secondary_emoji = '🟩 '
        elif change_24h < -3.5 or change_1h < -2.0:
            secondary_emoji = '🔻 '
        else:
            secondary_emoji = ''

        msg += f'{main_emoji} *{coin_name}* ({coin_abbr}):\n'
        msg += f'{Config.SPACING}{secondary_emoji}*{price:,}$*:\n'
        msg += f'{Config.SPACING}( {change_1h:,.2f}% *|* {change_24h:,.2f}% *|* {change_7d:,.2f}% )\n\n'

    return msg


class CoinMarketCupAPI:
    base_url = 'https://pro-api.coinmarketcap.com/{}'
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': Config.CMC_API_TOKEN}

    @staticmethod
    def get_coins(coins: list) -> dict | None:
        ids = ','.join([str(c) for c in coins])
        endpoint = f'v2/cryptocurrency/quotes/latest?id={ids}'
        request_url = CoinMarketCupAPI.base_url.format(endpoint)

        with requests.Session() as session:
            session.headers.update(CoinMarketCupAPI.headers)
            resp = session.get(request_url, params={'convert': 'USD'}).json()

        if resp:
            return resp['data']

        return
