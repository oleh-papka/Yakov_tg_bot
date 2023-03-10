from datetime import datetime

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src.crud.user import get_user_by_id
from src.handlers.days_passed import calc_date_diff, compose_passed_days_msg
from src.utils.db_utils import get_session
from src.utils.message_utils import escape_md2
from src.utils.time_utils import UserTime
import re


async def rus_losses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        user_time = UserTime.get_time_from_offset(user_model.timezone_offset)

    url = 'https://index.minfin.com.ua/ua/russian-invading/casualties/'
    response = requests.get(url)

    error_text = "Ситуація, не можу отримати дані з сайту..."
    if not response.ok:
        await message.reply_text(error_text)
        return

    soup = BeautifulSoup(response.text, 'lxml')
    data = soup.select('#idx-content > ul:nth-child(5) > li:nth-child(1)')[0]

    date = data.find('span', class_='black').text
    diff = calc_date_diff(datetime(2022, 2, 24), user_time['dt'])
    rel_time = compose_passed_days_msg(diff, 'початку війни')
    losses_text = f'Втрати ₚосії станом на *{date}*:\n\n'

    loses = data.select('div')[0].find_all('li')
    if not loses:
        await message.reply_text(error_text)
        return

    for loss in loses:
        loss = loss.text

        numbers = re.findall(r'\d+', loss)
        for number in numbers:
            number_with_separator = f'{int(number):,}'
            loss = loss.replace(number, number_with_separator)

        if '(катери)' in loss:
            loss = loss.replace(' (катери)', '/катери')
        if 'близько' in loss:
            loss = loss.replace('близько ', '±')
        losses_text += loss.replace('(', '*(').replace(')', ')*') + '\n'

    losses_text += f'\n{rel_time}'
    losses_text = escape_md2(losses_text, ['*'])
    await message.reply_markdown_v2(losses_text)


ru_losses_handler = CommandHandler('ruloss', rus_losses)
