from telegram import Update
from telegram.ext import CallbackContext
from telegram.messageentity import MessageEntity


def escape_str_md2(msg: str, exclude: str | list | None = None, *exclude_additional: str | list | None) -> str:
    if exclude is None:
        exclude = []
    elif isinstance(exclude, str):
        if exclude == MessageEntity.TEXT_LINK:
            exclude = ['(', ')', '[', ']']
        else:
            exclude = [character for character in exclude]
    elif not isinstance(exclude, list):
        raise ValueError

    if exclude_additional:
        for i in exclude_additional:
            if isinstance(i, str):
                if i == MessageEntity.TEXT_LINK:
                    i = ['(', ')', '[', ']']
                else:
                    i = [character for character in exclude]

            exclude.extend(i)

    escape_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for character in escape_symbols:
        if character in exclude:
            continue
        msg = msg.replace(character, rf'\{character}')

    return msg


def send_chat_action(action_type: str):
    def send_action(func):
        def command_func(update: Update, context: CallbackContext, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action_type)
            return func(update, context, *args, **kwargs)

        return command_func

    return send_action
