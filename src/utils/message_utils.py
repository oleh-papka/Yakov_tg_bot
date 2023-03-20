from functools import wraps

from telegram.constants import ChatAction


def escape_md2(msg: str, exclude: list | None = None) -> str:
    exclude = [] if exclude is None else exclude
    escape_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for character in escape_symbols:
        if character in exclude:
            continue
        msg = msg.replace(character, rf'\{character}')

    return msg


def escape_md2_no_links(msg: str, exclude: list | None = None) -> str:
    link_symbols = ['(', ')', '[', ']']
    escape_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    if exclude is None:
        exclude = link_symbols
    else:
        exclude.extend(link_symbols)

    for character in escape_symbols:
        if character in exclude:
            continue
        msg = msg.replace(character, rf'\{character}')

    return msg


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context, *args, **kwargs)

        return command_func

    return decorator


send_typing_action = send_action(ChatAction.TYPING)
send_upload_photo_action = send_action(ChatAction.UPLOAD_PHOTO)
