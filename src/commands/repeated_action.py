import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (filters,
                          MessageHandler,
                          ConversationHandler,
                          CommandHandler,
                          ContextTypes,
                          CallbackQueryHandler)

from config import Config
from crud.repeated_action import create_action, get_actions, delete_action
from crud.user import create_or_update_user
from handlers.canel_conversation import cancel, cancel_back_keyboard
from utils.db_utils import get_session
from utils.message_utils import send_typing_action, escape_md2
from utils.repeated_action_utils import get_callback, get_action_name
from utils.time_utils import parse_action_time

ACTIONS_START, GET_ACTION, SET_ACTION, LIST_ACTIONS, DELETE_ACTION = 1, 2, 3, 4, 5

start_actions_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(f'Додати дію️ ⏲️', callback_data='add_action'),
        InlineKeyboardButton(f'Встановлені дії 📑', callback_data='list_actions')
    ],
    [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
])


@send_typing_action
async def repeated_actions_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    user = update.effective_user
    context.user_data['command_msg'] = message

    async with get_session() as session:
        await create_or_update_user(session, user)

    context.user_data['markup_msg'] = await message.reply_text('Що бажаєш зробити?',
                                                               reply_markup=start_actions_keyboard)

    return ACTIONS_START


@send_typing_action
async def add_repeated_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    markup_msg = context.user_data['markup_msg']

    await query.answer()

    actions_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f'Погода 🌦️', callback_data='weather'),
            InlineKeyboardButton(f'кацапи ☠️️', callback_data='rus_loses')
        ],
        [
            InlineKeyboardButton(f'Крипта 🪙', callback_data='crypto'),
            InlineKeyboardButton(f'Валюти 🇺🇦', callback_data='curr'),
        ],
        [InlineKeyboardButton('🔙 Назад', callback_data='back')],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ])

    rep_actions_text = ('Повторювані дії чудовий спосіб налаштувати щоденне '
                        'відтворення певної команди в заданий час.\n\n'
                        'Обери команду яку будемо повторювати:')

    context.user_data['markup_msg'] = await markup_msg.edit_text(rep_actions_text,
                                                                 reply_markup=actions_keyboard)

    return GET_ACTION


@send_typing_action
async def actions_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user = query.from_user
    markup_msg = context.user_data['markup_msg']

    await query.answer()

    id_map = {'nums': [], 'ids': []}

    async with get_session() as session:
        action_models = await get_actions(session, user_id=user.id)

    if len(action_models) != 0:
        action_btn = InlineKeyboardButton('Видалити дію 🗑️', callback_data='delete_action')
        actions_list_text = '🆗 Ось список усіх твоїх повторюваних дій:\n\n'

        for num, action in enumerate(action_models, start=1):
            actions_list_text += (f'{Config.SPACING}id: {num} *|* '
                                  f'{get_action_name(action.action)} *|* '
                                  f'{action.execution_time.strftime("%H:%M")}\n')

            id_map['nums'].append(num)
            id_map['ids'].append(action.id)

        returning = LIST_ACTIONS
    else:
        action_btn = InlineKeyboardButton(f'Додати дію️ ⏲️', callback_data='add_action')
        actions_list_text = ('🆗 Схоже у тебе немає жодної дії.\n\n'
                             'Бажаєш додати дію?')
        returning = ACTIONS_START

    actions_keyboard = InlineKeyboardMarkup([
        [action_btn],
        [InlineKeyboardButton('🔙 Назад', callback_data='back')],
        [InlineKeyboardButton('🚫 Відмінити', callback_data='cancel')]
    ])

    context.user_data['id_map'] = id_map
    context.user_data['markup_msg'] = await markup_msg.edit_text(escape_md2(actions_list_text, ['*', '`']),
                                                                 reply_markup=actions_keyboard,
                                                                 parse_mode=ParseMode.MARKDOWN_V2)

    return returning


@send_typing_action
async def delete_action_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    markup_msg = context.user_data['markup_msg']

    await query.answer()
    await markup_msg.edit_reply_markup()

    actions_delete_text = message.text
    actions_delete_text += '\n\nТоді, напиши *id* повторюваної дії, яку потрібно видалити:'

    context.user_data['markup_msg'] = await markup_msg.edit_text(escape_md2(actions_delete_text, ['*']),
                                                                 reply_markup=cancel_back_keyboard,
                                                                 parse_mode=ParseMode.MARKDOWN_V2)

    return DELETE_ACTION


@send_typing_action
async def delete_repeated_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.message
    markup_msg = context.user_data['markup_msg']
    id_map = context.user_data['id_map']

    await markup_msg.edit_reply_markup(reply_markup=None)
    user_input = message.text.strip()

    match = re.match(r'^\d+$', user_input)

    if not match:
        delete_action_error_text = '⚠ Cхоже *id* повторюваної дії вказано не вірно, спробуй ще раз нижче:'
        context.user_data['markup_msg'] = await message.reply_text(text=escape_md2(delete_action_error_text, ['*']),
                                                                   reply_markup=cancel_back_keyboard,
                                                                   parse_mode=ParseMode.MARKDOWN_V2)
        return DELETE_ACTION
    else:
        num_id = int(user_input)
        delete_action_error_text = ('⚠ Cхоже повторюваної дії із вказаним *id* немає, '
                                    'перевір *id* та спробуй ще раз нижче:')

        if num_id not in id_map['nums']:
            context.user_data['markup_msg'] = await message.reply_text(text=escape_md2(delete_action_error_text, ['*']),
                                                                       reply_markup=cancel_back_keyboard,
                                                                       parse_mode=ParseMode.MARKDOWN_V2)
            return DELETE_ACTION
        else:
            action_id = id_map['ids'][id_map['nums'].index(num_id)]

        async with get_session() as session:
            action_models = await get_actions(session, action_id=action_id)

        if len(action_models) == 0:
            context.user_data['markup_msg'] = await message.reply_text(text=escape_md2(delete_action_error_text, ['*']),
                                                                       reply_markup=cancel_back_keyboard,
                                                                       parse_mode=ParseMode.MARKDOWN_V2)
            return DELETE_ACTION
        else:
            action_model = action_models[0]

    async with get_session() as session:
        await delete_action(session, action_id=action_id)

    action_deleted_text = f'✅ Зроблено, дію *{get_action_name(action_model.action)}* з *id: {num_id}* видалено!'

    await message.reply_text(text=escape_md2(action_deleted_text, ['*']), parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data.clear()

    return ConversationHandler.END


@send_typing_action
async def set_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    markup_msg = context.user_data['markup_msg']
    context.user_data['action'] = query.data

    await query.answer()
    await markup_msg.edit_reply_markup()

    msg_text = (f'🆗 Продовжимо налаштування дії *{get_action_name(query.data)}*.\n\n'
                f'Напиши нижче час коли варто виконувати дану дію:')
    await message.edit_text(escape_md2(msg_text, ['*']),
                            reply_markup=cancel_back_keyboard,
                            parse_mode=ParseMode.MARKDOWN_V2)

    return SET_ACTION


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
        set_time_error_text = '⚠ Cхоже час вказано не вірно, спробуй ще раз:'
        context.user_data['markup_msg'] = await message.reply_text(text=set_time_error_text,
                                                                   reply_markup=cancel_back_keyboard)
        return SET_ACTION

    async with get_session() as session:
        action_models = await get_actions(session, user_id=user.id, action=action, execution_time=execution_time)
        if len(action_models):
            action_model = action_models[0]
            set_time_error_text = (f'⚠ Дія (*{get_action_name(action_model.action)}*, '
                                   f'*id: {action_model.id}*) уже існує із заданим часом відтворення.\n\n'
                                   f'Тому я вважатиму що це помилка 😉. Спробуй ще раз з іншим часом:')

            context.user_data['markup_msg'] = await message.reply_text(text=escape_md2(set_time_error_text, ['*']),
                                                                       reply_markup=cancel_back_keyboard,
                                                                       parse_mode=ParseMode.MARKDOWN_V2)
            return SET_ACTION

    async with get_session() as session:
        await create_action(session, user_id=user.id, action=action, execution_time=execution_time)

    context.job_queue.run_daily(get_callback(action), time=execution_time, chat_id=user.id)

    time_change_text = (f'✅ Зроблено, твоя дія *{get_action_name(action)}* буде повторюватись '
                        f'щодня о *{execution_time.strftime("%H:%M")}*')
    await message.reply_markdown_v2(text=escape_md2(time_change_text, ['*']))

    context.user_data.clear()

    return ConversationHandler.END


async def back_to_actions_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    settings_start_text = 'Шукаєш щось інше?\nОбери з нижче наведених опцій:'

    await query.edit_message_text(text=settings_start_text, reply_markup=start_actions_keyboard)

    return ACTIONS_START


repeated_actions_handler = ConversationHandler(
    entry_points=[CommandHandler('rep_action', repeated_actions_start)],
    states={
        ACTIONS_START: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(actions_preview, pattern='^list_actions$'),
            CallbackQueryHandler(add_repeated_action, pattern=r'^add_action$'),
        ],
        GET_ACTION: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_actions_start, pattern='^back$'),
            CallbackQueryHandler(set_action, pattern=r'\w')
        ],
        SET_ACTION: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_actions_start, pattern='^back$'),
            MessageHandler(filters.TEXT, set_action_time)
        ],
        LIST_ACTIONS: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_actions_start, pattern='^back$'),
            CallbackQueryHandler(delete_action_start, pattern='^delete_action$')
        ],
        DELETE_ACTION: [
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(back_to_actions_start, pattern='^back$'),
            MessageHandler(filters.TEXT, delete_repeated_action)
        ]
    },
    fallbacks=[
        MessageHandler(filters.ALL, cancel)
    ],
    conversation_timeout=300.0
)
