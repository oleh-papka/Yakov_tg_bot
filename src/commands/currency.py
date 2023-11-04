from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from crud.currency import get_curr_by_user_id
from crud.user import get_user_by_id
from models.errors import MinFinParseError, MinFinFetchError, Privat24APIError
from utils.currency_utils import MinFinScrapper, Privat24API, compose_currencies_msg
from utils.db_utils import get_session
from utils.message_utils import escape_md2, send_typing_action
from utils.time_utils import UserTime


@send_typing_action
async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        user_time = UserTime(offset=user_model.timezone_offset)
        ccy_models = await get_curr_by_user_id(session, user.id)

    ccy_text = f"Курси валют:\n\n"

    if not ccy_models:
        ccy_text = ('⚠ Жодної валюти не вказано для відстежування, щоб налаштувати'
                    ' команду, обери відповідні в нелаштуваннях - /settings')
        await message.reply_text(ccy_text)
        return

    try:
        ccy_data = MinFinScrapper.get_currencies_prices()
        ccy_data["USD"] |= Privat24API.get_usd_price()
    except (MinFinParseError, MinFinFetchError, Privat24APIError):
        await message.reply_text("Ситуація, не можу отримати дані...")
        return

    ccy_text += compose_currencies_msg(ccy_data, ccy_models)

    await message.reply_markdown_v2(escape_md2(ccy_text, exclude=['*', '_', '`']))


currency_command_handler = CommandHandler('currency', currency_command)


async def currency_callback(context: ContextTypes.DEFAULT_TYPE):
    async with get_session() as session:
        ccy_models = await get_curr_by_user_id(session, context.job.chat_id)

    ccy_text = f"Курси валют:\n\n"

    if not ccy_models:
        ccy_error_text = ('⚠ Жодної валюти не вказано для відстежування, щоб налаштувати'
                          ' команду, обери відповідні в нелаштуваннях - /settings')
        await context.bot.send_message(chat_id=context.job.chat_id,
                                       text=ccy_error_text,
                                       parse_mode=ParseMode.MARKDOWN_V2)
        return

    try:
        ccy_data = MinFinScrapper.get_currencies_prices()
        ccy_data["USD"] |= Privat24API.get_usd_price()
    except (MinFinParseError, MinFinFetchError, Privat24APIError):
        return

    ccy_text += compose_currencies_msg(ccy_data, ccy_models)

    await context.bot.send_message(chat_id=context.job.chat_id,
                                   text=escape_md2(ccy_text, exclude=['*', '_', '`']),
                                   parse_mode=ParseMode.MARKDOWN_V2)
