'''
Collection of commonly used functions/routines.
'''

import os
from pathlib import Path
import logging

import flask.logging
import flask


def get_secret(name: str, default: str = '') -> str:
    '''
    Get a secret.

    First this will check for `/run/secrets/{name}` for a docker secret. Then it will check for an
    environment variable with the prefix `APP_` and `name` in uppercase and dashes replaced with
    underscores.

        get_secret('my-secret')
        -> /run/secret/my-secret
        -> os.environ['APP_MY_SECRET']
    '''
    file_path = Path(f'/run/secrets/{name}')
    env_var = 'APP_'f'{name.upper().replace("-", "_")}'
    ret = default
    if file_path.exists():
        ret = file_path.read_text(encoding='utf-8')
        ret = ret.splitlines()[0]
        ret = ret.split()[0]
    elif env_var in os.environ:
        ret = os.environ.get(env_var, default)
    return ret


class _Cached:
    _LOGGER_NAME = 'api'

    def __init__(self) -> None:
        self._log_init = False

    @property
    def logger(self) -> logging.Logger:
        ''' Get a logger instance. '''
        log = flask.logging.create_logger(flask.current_app)
        return log


GLOBALS = _Cached()
