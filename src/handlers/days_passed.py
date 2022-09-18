import re
from datetime import datetime

from dateutil import relativedelta
from telegram import Update, ChatAction
from telegram.ext import CallbackContext, MessageHandler, Filters

from config import Config
from crud.user import manage_user
from utils.db_utils import create_session
from utils.message_utils import send_chat_action

from_date_regex = re.compile(r'^\d{1,2}(\.|-|/|\s)\d{1,2}(\.|-|/|\s)\d{4}$')
from_to_date_regex = re.compile(
    r'^\d{1,2}(\.|-|/|\s)\d{1,2}(\.|-|/|\s)\d{4}\s+\d{1,2}(\.|-|/|\s)\d{1,2}(\.|-|/|\s)\d{4}$')


def calc_date_diff(t1: datetime, t2: datetime | None = None) -> tuple:
    if t2 is None:
        t2 = datetime.now()

    if (t1.tzinfo and not t2.tzinfo) or (not t1.tzinfo and t2.tzinfo):
        t1 = t1.replace(tzinfo=None)
        t2 = t2.replace(tzinfo=None)

    delta = relativedelta.relativedelta(t2, t1)
    all_days = (t2 - t1).days + 1  # Add 1 day to be inclusive
    all_months = (delta.years * 12) + delta.months

    return all_days, all_months, delta


def parse_date(msg: str) -> tuple | None:
    msg = msg.strip()
    if re.match(from_date_regex, msg):
        r = msg.replace('.', ' ').replace('-', ' ').replace('/', ' ').split()
        day, month, year = (int(el) for el in r)

        if month > 12:
            day, month = month, day

        return datetime(year, month, day),

    elif re.match(from_to_date_regex, msg):
        msg = re.sub(r'\s+', ' ', msg)
        r = msg.replace('.', ' ').replace('-', ' ').replace('/', ' ').split()

        day1, month1, year1, day2, month2, year2 = (int(el) for el in r)
        if month1 > 12:
            day1, month1 = month1, day1
        if month2 > 12:
            day2, month2 = month2, day2

        date1 = datetime(year1, month1, day1)
        date2 = datetime(year2, month2, day2)

        if date1 > date2:
            date1, date2 = date2, date1

        return date1, date2

    else:
        return


def compose_passed_days_msg(data: tuple, desc: str | None = None) -> str:
    all_days, all_months, delta = data

    if desc is None:
        desc = 'даного моменту'
    else:
        desc = f'моменту {desc}'

    msg = f'Із {desc} пройшло:\n{Config.SPACING}'

    if delta.years:
        msg += f'{delta.years} років, '

    msg += f'{delta.months} місяців'

    if all_months > 12:
        msg += f' (загалом {all_months}), '
    else:
        msg += ', '

    if all_days > 28:
        msg += f'{delta.days} днів (загалом {all_days})\n\n'
    else:
        msg += f'{delta.days} днів\n\n'

    return msg


@create_session
@send_chat_action(ChatAction.TYPING)
def days_passed(update: Update, context: CallbackContext, db):
    message = update.message
    user = update.effective_user
    text = message.text
    manage_user(db, user)

    parsed_date = parse_date(text)
    msg = compose_passed_days_msg(data=calc_date_diff(*parsed_date))
    message.reply_text(msg, quote=True)


days_passed_handler = MessageHandler(
    Filters.regex(from_date_regex) | Filters.regex(from_to_date_regex),
    days_passed)
