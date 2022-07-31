from telegram import LabeledPrice, Update, ParseMode
from telegram.ext import CommandHandler, PreCheckoutQueryHandler, MessageHandler, Filters, CallbackContext

from config import Config
from utils import clear_str_md2


def tip_developer(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    title = 'Купити смаколиків розробнику'
    description = 'Я старався'
    payload = "Custom-Payload"
    provider_token = '632593626:TEST:sandbox_i29859238551'
    currency = "UAH"

    price = 50

    prices = [LabeledPrice('На щось смачненьке', price * 100)]
    max_tip_amount = 10000
    suggested_tip_amounts = [1000, 5000, 10000]

    user = update.message.from_user

    context.bot.send_invoice(
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
        photo_url='https://images.unsplash.com/photo-1588339721875-709c2135fc49?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80',
        photo_size='1000',
        photo_height=400,
        photo_width=400
    )


def payment_precheckout(update: Update, context: CallbackContext):
    query = update.pre_checkout_query

    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Щось пішло не так...")
    else:
        query.answer(ok=True)


def successful_payment(update: Update, context: CallbackContext):
    message = update.message
    payment = message.successful_payment
    user = message.from_user

    message.reply_text("✅ Чотенько, дякую за грошенятка!")

    msg = f'Не повіриш! Добра душа [{user.first_name}](tg://user?id={user.id}) ' \
          f'передала тобі пару гривників \({payment.total_amount / 100:g} {payment.currency}\)!'

    context.bot.send_message(Config.OWNER_ID, clear_str_md2(msg, exclude=['[', ']', '(', ')']),
                             parse_mode=ParseMode.MARKDOWN_V2)


tip_developer_handler = CommandHandler("tip_developer", tip_developer)
precheckout_handler = PreCheckoutQueryHandler(payment_precheckout)
successful_payment_handler = MessageHandler(Filters.successful_payment, successful_payment)
