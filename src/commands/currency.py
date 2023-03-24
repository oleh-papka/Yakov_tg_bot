from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from src.crud.currency import get_curr_by_user_id
from src.crud.user import get_user_by_id
from src.utils.currency_utils import get_min_fin_price, get_privat_usd_price, compose_output
from src.utils.db_utils import get_session
from src.utils.message_utils import escape_md2, send_typing_action
from src.utils.time_utils import UserTime


@send_typing_action
async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        user_time = UserTime(offset=user_model.timezone_offset)
        ccy_models = await get_curr_by_user_id(session, user.id)

    ccy_text = f"Курси валют (*{user_time.date_repr(style_flag=True)}*)\n\n"
    error_text = "Ситуація, не можу отримати дані із сайту..."

    if not ccy_models:
        ccy_text = ('⚠ Жодної валюти не вказано для відстежування, щоб налаштувати'
                    ' команду, обери відповідні в нелаштуваннях - /settings')
        await message.reply_text(ccy_text)
        return

    ccy_data = get_min_fin_price()
    ccy_data["USD"] |= get_privat_usd_price()

    ccy_text += compose_output(ccy_data, ccy_models)

    await message.reply_markdown_v2(escape_md2(ccy_text, exclude=['*', '_']))


currency_command_handler = CommandHandler('currency', currency)
