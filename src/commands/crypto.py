import requests
from telegram import Update, ChatAction, ParseMode
from telegram.ext import CommandHandler, CallbackContext

from config import Config
from utils import clear_str_md2, get_user_time


def get_crypto_data(positions: int = 15) -> tuple | None:
    params_usd = {'start': '1', 'limit': str(positions), 'convert': 'USD'}
    params_uah = {'start': '1', 'limit': str(positions), 'convert': 'UAH'}

    api_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': Config.CMC_API_TOKEN}

    with requests.Session() as session:
        session.headers.update(headers)
        usd_resp = session.get(api_url, params=params_usd)
        uah_resp = session.get(api_url, params=params_uah)

    if usd_resp.ok and uah_resp.ok:
        return usd_resp.json(), uah_resp.json(), positions
    else:
        return None


def compose_crypto_msg(usd, uah, positions: int) -> str:
    time = get_user_time()['time']
    msg = f'CoinMarketCup дані на (*{time}*):\n\n'

    for i in range(positions):
        coin_id = usd['data'][i]['id']
        if coin_id not in Config.CRYPTO_COIN_IDS:
            continue

        coin_name = usd['data'][i]['name']
        coin_abbr = usd['data'][i]['symbol']

        price_usd = round(usd['data'][i]['quote']['USD']['price'], 1)
        price_uah = round(uah['data'][i]['quote']['UAH']['price'], 1)

        change_1h = round(usd['data'][i]['quote']['USD']['percent_change_1h'], 2)
        change_24h = round(usd['data'][i]['quote']['USD']['percent_change_24h'], 2)
        change_7d = round(usd['data'][i]['quote']['USD']['percent_change_7d'], 2)

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
        msg += f'{Config.SPACING}{secondary_emoji}*{price_usd:,}$* (_{price_uah:,}₴_):\n'
        msg += f'{Config.SPACING}( {change_1h:0.2f}% *|* {change_24h:0.2f}% *|* {change_7d:0.2f}% )\n\n'

    return clear_str_md2(msg, ['*', '_'])


def crypto_command(update: Update, context: CallbackContext) -> None:
    message = update.message

    message.reply_chat_action(ChatAction.TYPING)
    crypto_data = get_crypto_data()
    if crypto_data is None:
        msg = '⚠ Щось пішло не так, немає відповіді від API...'
        message.reply_text(msg)
        return
    else:
        message.reply_text(compose_crypto_msg(*crypto_data), parse_mode=ParseMode.MARKDOWN_V2)


crypto_command_handler = CommandHandler('crypto', crypto_command)
