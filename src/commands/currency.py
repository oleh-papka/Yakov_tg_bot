import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src.config import Config
from src.crud.currency import get_curr_by_user_id
from src.crud.user import get_user_by_id
from src.utils.db_utils import get_session
from src.utils.message_utils import escape_md2, send_typing_action
from src.utils.time_utils import UserTime


@send_typing_action
async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        user_time = UserTime.get_time_from_offset(user_model.timezone_offset)
        curr_models = await get_curr_by_user_id(session, update.effective_user.id)

    url = "https://minfin.com.ua/ua/currency/{}"

    curr_text = f"Дані по валюті на (*{user_time['date_time']}*)\n\n"
    error_text = "Ситуація, не можу отримати дані із сайту..."

    if not curr_models:
        curr_text = ('⚠ Жодної валюти не вказано для відстежування, щоб налаштувати'
                     ' команду, обери відповідні в нелаштуваннях - /settings')
        await message.reply_text(curr_text)
        return

    for model in curr_models:
        curr = model.name
        emoji = model.symbol
        response = requests.get(url.format(curr))

        if not response.ok:
            await message.reply_text(error_text)
            return

        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.select("body > main > div.mfz-container > div > div.mfz-col-content > "
                            "div > section:nth-child(3) > div.mfm-grey-bg > table")

        if not table:
            await message.reply_text(error_text)
            return

        rows = table[0].find_all('tr')[1:]
        if not rows:
            await message.reply_text(error_text)
            return

        curr_text += f'{emoji} *{curr.upper()}:*\n'

        for row in rows[:-1]:  # Get all prices without НБУ price
            tds = row.find_all('td')
            market_type = tds[0].a.text.capitalize()
            buy = float(tds[1].span.text.split('\n')[0])
            sell = float(tds[2].span.text.split('\n')[0])
            curr_text += f'{Config.SPACING}{market_type}:  _{buy:0.2f}₴_ | _{sell:0.2f}₴_\n'

        # Get НБУ price
        td = rows[-1].find_all('td')
        market_type = td[0].a.text
        price = float(td[1].span.text.split('\n')[0])
        curr_text += f'{Config.SPACING}{market_type}:  _{price:0.2f}₴_\n'

        curr_text += '\n'

    await message.reply_markdown_v2(escape_md2(curr_text, exclude=['*', '_']))


currency_command_handler = CommandHandler('currency', currency)
