from sqlalchemy.orm import Session
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


@send_chat_action(ChatAction.TYPING)
def crypto_command(update: Update, context: CallbackContext, db: Session) -> None:
    message = update.message
    user = update.effective_user
    user_model = create_or_update_user(db, user)
    coins = [coin.id for coin in user_model.crypto_currency]

    if not coins:
        msg = ('⚠ Жодної криптовалюти не вказано для відстежування, щоб '
               'налаштувати команду, обери відповідні в нелаштуваннях - /settings')
        message.reply_text(msg)
        return

    crypto_data = get_crypto_data()
    if crypto_data is None:
        msg = '⚠ Щось пішло не так, немає відповіді від API...'
        message.reply_text(msg)
        return
    else:
        time = UserTime.get_time_from_offset(user_model.timezone_offset)['date_time']
        msg = f'CoinMarketCup дані на (*{time}*):\n\n'
        msg += compose_crypto_msg(*crypto_data, coins=coins)
        message.reply_text(escape_str_md2(msg, exclude=['*', '_']), parse_mode=ParseMode.MARKDOWN_V2)


crypto_command_handler = CommandHandler('crypto', crypto_command)
