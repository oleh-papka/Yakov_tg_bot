import os
from typing import Any


def load_env_variable(name: str, convert_type: Any = None, raise_if_none: bool = True) -> Any:
    env_var = os.environ.get(name)
    if env_var is None and raise_if_none:
        raise ValueError(f"Env variable '{name}' is not configured!")
    elif env_var is None and raise_if_none is False:
        return

    if convert_type is not None:
        env_var = convert_type(env_var)

    return env_var
