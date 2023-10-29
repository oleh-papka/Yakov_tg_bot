import os
from typing import Any

from models.errors import EnvNotProvidedError


def load_env_variable(name: str, convert_to_type: Any = None, raise_if_none: bool = True) -> Any | None:
    env_var = os.environ.get(name)

    if env_var is None and raise_if_none:
        raise EnvNotProvidedError(f"Env variable '{name}' is not provided! Please configure it in 'config.py' file.")

    if env_var is None and raise_if_none is False:
        return None

    if convert_to_type is not None:
        env_var = convert_to_type(env_var)

    return env_var
