import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (filters,
                          MessageHandler,
                          ConversationHandler,
                          CommandHandler,
                          ContextTypes,
                          CallbackQueryHandler)

from crud.repeated_action import create_action
from crud.user import create_or_update_user
from handlers.canel_conversation import cancel, cancel_keyboard, cancel_back_keyboard
from utils.db_utils import get_session
from utils.message_utils import send_typing_action
from utils.repeated_action_utils import get_callback
from utils.time_utils import parse_action_time

GET_ACTION, GET_TIME = 1, 2


@send_typing_action
async def repeated_actions_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    actions_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f'Погода 🌦️', callback_data='weather'),
            InlineKeyboardButton(f'кацапи ☠️️', callback_data='rus_loses')
        ],
        [
            InlineKeyboardButton(f'Крипта 🪙', callback_data='crypto'),
            InlineKeyboardButton(f'Валюти 🇺🇦', callback_data='curr'),
        ],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ])

    context.user_data['markup_msg'] = await message.reply_text('Ок, Обери з нижче наведених опцій:',
                                                               reply_markup=actions_keyboard)

    return GET_ACTION


@send_typing_action
async def set_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    markup_msg = context.user_data['markup_msg']
    context.user_data['action'] = query.data

    await query.answer()
    await markup_msg.edit_reply_markup()

    msg_text = f'✅ Ок, продовжимо. Напиши нижче час коли варто виконувати дану дію:'
    await message.edit_text(msg_text, reply_markup=cancel_keyboard)

    return GET_TIME


@send_typing_action
async def set_action_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    markup_msg = context.user_data['markup_msg']
    action = context.user_data['action']

    await markup_msg.edit_reply_markup(reply_markup=None)
    user_input = message.text.strip()

    execution_time = parse_action_time(user_input)
    match = re.match(r'^[0-2]?[0-9](\s|:)[0-5][0-9]$', user_input)

    if not match or not execution_time:
        set_time_error_text = '⚠ Cхоже час вказано не вірно, спробуй ще раз.'
        context.user_data['markup_msg'] = await message.reply_text(text=set_time_error_text,
                                                                   reply_markup=cancel_back_keyboard)
        return GET_TIME

    context.job_queue.run_daily(get_callback(action), time=execution_time, chat_id=user.id)

    async with get_session() as session:
        await create_action(session, user_id=user.id, action=action, execution_time=execution_time)

    time_change_text = f'✅ Зроблено, твоя дія буде повторюватись щодня о {user_input}'
    await message.reply_text(text=time_change_text)

    context.user_data.clear()

    return ConversationHandler.END


repeated_actions_handler = ConversationHandler(
    entry_points=[CommandHandler('rep_action', repeated_actions_start)],
    states={
        GET_ACTION: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(set_action, pattern=r'\w')
        ],
        GET_TIME: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            MessageHandler(filters.TEXT, set_action_time)
        ],
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)
