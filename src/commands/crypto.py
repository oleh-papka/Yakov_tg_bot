from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from config import Config
from src.crud.user import get_user_by_id
from src.utils.db_utils import get_session
from src.utils.message_utils import escape_md2, send_typing_action
from src.utils.time_utils import UserTime
from utils.binance_utils import compose_binance_msg, BinanceAPI
from utils.cmc_utils import CoinMarketCupAPI, compose_coins_msg


@send_typing_action
async def crypto_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user = update.effective_user

    async with get_session() as session:
        user_model = await get_user_by_id(session, user.id)
        coins = [coin.id for coin in user_model.crypto_currency]

    if not coins:
        coins_not_found_text = ('⚠ Жодної криптовалюти не вказано для відстежування, щоб '
                                'налаштувати команду, обери відповідні в нелаштуваннях - /settings')
        await message.reply_text(coins_not_found_text)
        return

    crypto_data = CoinMarketCupAPI.get_coins(coins)
    if crypto_data is None:
        error_text = '⚠ Щось пішло не так, немає відповіді від API...'
        await message.reply_text(error_text)
        return

    time = UserTime.get_time_from_offset(user_model.timezone_offset)['date_time']
    crypto_text = f'CoinMarketCup дані на (*{time}*):\n\n'
    crypto_text += compose_coins_msg(crypto_data)

    if user.id == Config.OWNER_ID:
        binance_client = BinanceAPI()
        wallet_data = binance_client.get_funding_wallet()

        crypto_text += compose_binance_msg(wallet_data, )

    await message.reply_markdown_v2(escape_md2(crypto_text, exclude=['*', '_']))


crypto_command_handler = CommandHandler('crypto', crypto_command)
