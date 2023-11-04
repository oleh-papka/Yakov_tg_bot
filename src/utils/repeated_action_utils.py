from telegram.ext import ContextTypes
from telegram.ext._utils.types import JobCallback, CCT

from commands.crypto import crypto_callback
from commands.currency import currency_callback
from commands.ru_losses import rus_losses_callback
from commands.weather import weather_callback
from crud.repeated_action import get_actions
from utils.db_utils import get_session


def get_callback(callback_name: str) -> JobCallback[CCT]:
    if callback_name == 'weather':
        return weather_callback
    elif callback_name == 'rus_loses':
        return rus_losses_callback
    elif callback_name == 'crypto':
        return crypto_callback
    elif callback_name == 'curr':
        return currency_callback


async def register_actions_callback(context: ContextTypes.DEFAULT_TYPE):
    async with get_session() as session:
        action_models = await get_actions(session)

    for action in action_models:
        context.job_queue.run_once(get_callback(action.action), when=action.execution_time, chat_id=action.user_id)
