from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, \
    filters

from config import Config
from crud.user import create_or_update_user, get_all_users, update_user
from handlers.canel_conversation import cancel
from utils.db_utils import get_session
from utils.message_utils import send_typing_action

GET_MESSAGE, SEND_MESSAGE = 1, 2


@send_typing_action
async def message_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = message.from_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    if user.id != Config.OWNER_ID:
        await message.reply_text('⚠️ У тебе немає прав на виконання цієї команди!')
        return ConversationHandler.END

    resp_keyboard = [
        [InlineKeyboardButton('🚫 Відміна', callback_data='cancel')]
    ]

    reply_keyboard = InlineKeyboardMarkup(resp_keyboard)

    profile_start_text = '🆗 Гаразд, будемо сповіщати усіх користувачів.\n\nНадішли текст цього повідомлення нижче:'
    context.user_data['markup_msg'] = await message.reply_text(profile_start_text, reply_markup=reply_keyboard)

    return GET_MESSAGE


@send_typing_action
async def message_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    context.user_data['message_text'] = message.text

    if query := context.user_data.get('send_to_query'):
        await query.edit_message_reply_markup()

    confirmation_keyboard = [
        [
            InlineKeyboardButton('Підтвердити ✅', callback_data='confirm'),
            InlineKeyboardButton('Редагувати 📝', callback_data='edit')
        ],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ]

    reply_keyboard = InlineKeyboardMarkup(confirmation_keyboard)

    await message.reply_text('Впевнений, надіслати дане повідомлення?',
                             reply_markup=reply_keyboard,
                             reply_to_message_id=message.message_id)

    return SEND_MESSAGE


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    msg_text = context.user_data['message_text']

    sending_text = '🆗 Уже надсилаю...'
    await query.edit_message_text(sending_text, reply_markup=None)

    async with get_session() as session:
        users = await get_all_users(session, True)

    users_count = len(users)
    decr = 0

    for number, user in enumerate(users):
        try:
            await context.bot.send_message(user.id, msg_text)
        except:
            async with get_session() as session:
                await update_user(session, user, {'active': False})
            users_count -= 1
            decr -= 1

        number += decr
        tmp_msg = sending_text + f'\n\nНадіслано {number + 1} із {users_count}'
        await query.edit_message_text(tmp_msg)

    sending_text = f'✅ Єєєєй! Уже завершив, усі ({users_count}) користувачі отримали твоє повідомлення.'

    await query.edit_message_text(sending_text)

    context.user_data.clear()
    return ConversationHandler.END


async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    edit_text = '🆗 Надішли у наступному повідомленні відповідно змінене.'
    await query.edit_message_text(edit_text, reply_markup=None)

    if 'send_to_query' in context.user_data:
        del context.user_data['send_to_query']

    return GET_MESSAGE


profile_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('message_users', message_users)],
    states={
        GET_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(filters.COMMAND, cancel),
            MessageHandler(filters.TEXT, message_check)
        ],
        SEND_MESSAGE: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(send_message, pattern='^confirm$'),
            CallbackQueryHandler(edit_message, pattern='^edit$')
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=600.0
)
