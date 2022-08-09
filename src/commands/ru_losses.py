import requests
from bs4 import BeautifulSoup
from telegram import ParseMode, ChatAction, Update
from telegram.ext import CommandHandler, CallbackContext

from crud.user import auto_create_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action, escape_str_md2


@create_session
@send_chat_action(ChatAction.TYPING)
def rus_losses(update: Update, context: CallbackContext, db):
    message = update.message
    user = message.from_user
    auto_create_user(db, user)

    url = 'https://index.minfin.com.ua/ua/russian-invading/casualties/'
    response = requests.get(url)

    error_msg = "Ситуація, не можу отримати дані з сайту..."
    if not response.ok:
        return message.reply_text(error_msg)

    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.select('#idx-content > ul:nth-child(5) > li:nth-child(1)')[0]

    date = data.find('span', class_='black').text
    msg = f'Втрати ₚосії станом на *{date}*:\n\n'

    loses = data.select('div')[0].find_all('li')
    if not loses:
        return message.reply_text(error_msg)

    for loss in loses:
        loss = loss.text
        if '(катери)' in loss:
            loss = loss.replace(' (катери)', '/катери')
        if 'близько' in loss:
            loss = loss.replace('близько ', '±')
        msg += loss.replace('(', '*(').replace(')', ')*') + '\n'

    message.reply_text(escape_str_md2(msg, ['*']), parse_mode=ParseMode.MARKDOWN_V2)


ru_losses_handler = CommandHandler('ruloss', rus_losses)
