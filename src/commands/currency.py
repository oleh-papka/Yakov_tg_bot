import requests
from bs4 import BeautifulSoup
from telegram import Update, ChatAction, ParseMode, MessageEntity
from telegram.ext import CallbackContext, CommandHandler

from config import Config
from crud.user import add_user_to_db
from utils import escape_str_md2
from utils.message_utils import send_chat_action


@add_user_to_db
@send_chat_action(ChatAction.TYPING)
def currency(update: Update, context: CallbackContext):
    message = update.message

    currencies_emoji_mapping = {
        'usd': '🇺🇸',
        'eur': '🇪🇺',
        'pln': '🇵🇱'
    }
    url = "https://minfin.com.ua/ua/currency/{}"
    msg = ''
    err_msg = "Ситуація, не можу отримати дані із сайту..."

    for curr, emoji in currencies_emoji_mapping.items():
        response = requests.get(url.format(curr))

        if not response.ok:
            return message.reply_text(err_msg)

        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.select(
            "body > main > div.mfz-container > div > div.mfz-col-content > div > section:nth-child(3) > "
            "div.mfm-grey-bg > table")

        if not table:
            return message.reply_text(err_msg)

        rows = table[0].find_all('tr')[1:]
        if not rows:
            return message.reply_text(err_msg)

        msg += f'{emoji} *{curr.upper()}:*\n'

        for row in rows[:-1]:  # Get all prices without НБУ price
            tds = row.find_all('td')
            market_type = tds[0].a.text.capitalize()
            buy = float(tds[1].span.text.split('\n')[0])
            sell = float(tds[2].span.text.split('\n')[0])
            msg += f'{Config.SPACING}{market_type}:  _{buy:0.2f}₴_ | _{sell:0.2f}₴_\n'

        # Get НБУ price
        td = rows[-1].find_all('td')
        market_type = td[0].a.text
        price = float(td[1].span.text.split('\n')[0])
        msg += f'{Config.SPACING}{market_type}:  _{price:0.2f}₴_\n'

        msg += '\n'

    message.reply_text(escape_str_md2(msg, exclude=['*', '_']), parse_mode=ParseMode.MARKDOWN_V2)


currency_command_handler = CommandHandler('currency', currency)
