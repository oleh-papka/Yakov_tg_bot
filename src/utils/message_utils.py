from telegram import Update
from telegram.ext import CallbackContext


def escape_md2(msg: str, exclude: list | None = None) -> str:
    exclude = [] if exclude is None else exclude
    escape_symbols = ['_', '*', '[', ']',
                      '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for character in escape_symbols:
        if character in exclude:
            continue
        msg = msg.replace(character, rf'\{character}')

    return msg


def escape_md2_no_links(msg: str, exclude: list | None = None) -> str:
    link_symbols = ['(', ')', '[', ']']
    escape_symbols = ['_', '*', '[', ']',
                      '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    if exclude is None:
        exclude = link_symbols
    else:
        exclude.extend(link_symbols)

    for character in escape_symbols:
        if character in exclude:
            continue
        msg = msg.replace(character, rf'\{character}')

    return msg


def send_chat_action(action_type: str):
    def send_action(func):
        def command_func(update: Update, context: CallbackContext, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action_type)
            return func(update, context, *args, **kwargs)

        return command_func

    return send_action
