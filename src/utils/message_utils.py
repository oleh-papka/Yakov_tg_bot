def clear_str_md2(msg: str, exclude: list | None = None) -> str:
    if exclude is None:
        exclude = []

    escape_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for character in escape_symbols:
        if character in exclude:
            continue
        msg = msg.replace(character, rf'\{character}')

    return msg
