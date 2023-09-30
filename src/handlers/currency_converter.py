import re

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from src.config import Config
from src.utils.currency_utils import Privat24API, get_min_fin_price
from src.utils.message_utils import send_typing_action, escape_md2

from_uah_to_usd = re.compile(r'^\d+[,.]?\d+\s?(uah|грн)$')
from_usd_to_uah = re.compile(r'^\d+[,.]?\d+\s?(usd|дол)$')


@send_typing_action
async def currency_converter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user_text = message.text.lower()
    amount = float(re.sub('\s?(uah|грн|usd|дол)', '', user_text).replace(',', '.'))

    ccy_data = get_min_fin_price()
    ccy_data["USD"] |= Privat24API.get_usd_price()

    usd_data = ccy_data["USD"]

    if 'uah' in user_text or 'грн' in user_text:  # converting uah to usd
        text = f"🧮 *{amount} UAH в USD:*\n"
        nb_text = ""

        for market_type, price in usd_data.items():
            if len(price) == 2:
                text += f"{Config.SPACING_SMALL}{market_type}: (_{price[1]:,.2f}₴_) -> *{amount / price[1]:,.2f}$*  \n"
            else:
                nb_text = f"{Config.SPACING_SMALL}{market_type}: (_{price[0]:,.2f}₴_) -> *{amount / price[0]:,.2f}$*\n"

        text += f"\n{nb_text}"

    else:  # converting usd to uah
        text = f"🧮 *{amount} USD в UAH:*\n"
        nb_text = ""

        for market_type, price in usd_data.items():
            if len(price) == 2:
                text += f"{Config.SPACING_SMALL}{market_type}: (_{price[0]:,.2f}₴_) -> *{amount * price[0]:,.2f}₴*\n"
            else:
                nb_text = f"{Config.SPACING_SMALL}{market_type}: (_{price[0]:,.2f}₴_) -> *{amount * price[0]:,.2f}₴*\n"

        text += f"\n{nb_text}"

    await message.reply_markdown_v2(escape_md2(text, exclude=['_', '*']), quote=True)


currency_convertor_handler = MessageHandler(filters.Regex(from_uah_to_usd) | filters.Regex(from_usd_to_uah),
                                            currency_converter)
