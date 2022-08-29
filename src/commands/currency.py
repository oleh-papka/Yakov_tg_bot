import requests
from bs4 import BeautifulSoup
from telegram import Update, ChatAction, ParseMode
from telegram.ext import CallbackContext, CommandHandler

from config import Config
from crud.currency import get_curr_by_user
from crud.user import auto_create_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action, escape_str_md2
from utils.time_utils import get_time_from_offset


@create_session
@send_chat_action(ChatAction.TYPING)
def currency(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    user_model = auto_create_user(db, user)
    user_time = get_time_from_offset(user_model.timezone_offset)

    url = "https://minfin.com.ua/ua/currency/{}"

    msg = f"Дані по валюті на (*{user_time['date_time']}*)\n\n"
    err_msg = "Ситуація, не можу отримати дані із сайту..."

    curr_models = get_curr_by_user(db, update.effective_user.id)

    if not curr_models:
        msg = '⚠ Жодної валюти не вказано для відстежування, ' \
              'щоб налаштувати команду, обери відповідні в нелаштуваннях - /settings'
        message.reply_text(msg)
        return

    for model in curr_models:
        curr = model.name
        emoji = model.symbol
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
