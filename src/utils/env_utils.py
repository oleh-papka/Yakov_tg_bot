import os
from typing import Any


def load_env_variable(name: str, convert_to_type: Any = None, error_if_none: bool = True) -> Any | None:
    env_var = os.environ.get(name)

    if env_var is None and error_if_none:
        raise ValueError(f"Env variable '{name}' is not configured!")

    if env_var is None and error_if_none is False:
        return None

    if convert_to_type is not None:
        env_var = convert_to_type(env_var)

    return env_var
