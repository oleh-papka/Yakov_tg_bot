from telegram import Update, LabeledPrice
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, PreCheckoutQueryHandler, MessageHandler, filters

from src.config import Config
from src.crud.user import create_or_update_user
from src.utils import escape_md2_no_links
from src.utils.db_utils import get_session


async def tip_developer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user = update.effective_user

    async with get_session() as session:
        await create_or_update_user(session, user)

    title = 'Купити смаколиків розробнику'
    description = 'Я старався'
    payload = "Custom-Payload"
    provider_token = '632593626:TEST:sandbox_i29859238551'
    currency = "UAH"
    price = 50
    prices = [LabeledPrice('На щось смачненьке', price * 100)]
    max_tip_amount = 10000
    suggested_tip_amounts = [1000, 5000, 10000]

    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices,
        max_tip_amount=max_tip_amount,
        suggested_tip_amounts=suggested_tip_amounts,
        start_parameter='tip_developer',
        photo_url=('https://images.unsplash.com/photo-1588339721875-709c2135'
                   'fc49?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8'
                   'fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80'),
        photo_size='1000',
        photo_height=400,
        photo_width=400
    )


async def payment_precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query

    if query.invoice_payload != 'Custom-Payload':
        await query.answer(ok=False, error_message="Щось пішло не так...")
    else:
        await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    payment = message.successful_payment
    user = message.from_user

    money_sent_text = (f'Не повіриш! Добра душа [{user.first_name}](tg://user?id={user.id}) '
                       f'передала тобі пару гривників \({payment.total_amount / 100:g} {payment.currency}\)!')

    await message.reply_text("✅ Чотенько, дякую за грошенятка!")
    await context.bot.send_message(Config.OWNER_ID, escape_md2_no_links(money_sent_text),
                                   parse_mode=ParseMode.MARKDOWN_V2)


tip_developer_handler = CommandHandler("tip_developer", tip_developer)
precheckout_handler = PreCheckoutQueryHandler(payment_precheckout)
successful_payment_handler = MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
