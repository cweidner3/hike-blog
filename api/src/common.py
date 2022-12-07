'''
Collection of commonly used functions/routines.
'''

from datetime import datetime
import io
import logging
import os
from pathlib import Path
import re
from typing import Any, Dict, Optional, Union

import PIL.ExifTags
import PIL.Image
import flask
import flask.logging
import pytz
import werkzeug.exceptions


EXIF_TIME_PAT = re.compile(r'^(\d{4}):(\d{2}):(\d{2})')

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

    _LUT = {
        'db': {
            'dialect': 'DB_DIALECT',
            'host': 'DB_HOST',
            'port': 'DB_PORT',
            'name': 'DB_NAME',
            'user': 'DB_USER',
            'pass': 'DB_PASS',
            'passfile': 'DB_PASS_FILE',
        },
        'app': {
            'mode': 'APP_MODE',
            'secret': 'APP_SECRET',
            'secretfile': 'APP_SECRET_FILE',
        },
    }

    def __init__(self) -> None:
        self._log_init = False

    @property
    def logger(self) -> logging.Logger:
        ''' Get a logger instance. '''
        log = flask.logging.create_logger(flask.current_app)
        return log

    def get_env(self, section: str, key: str, default: Optional[str] = None) -> str:
        if key.endswith('file') and self._LUT[section][key] not in os.environ:
            key = key[:-4]
        env_var = self._LUT[section][key]
        ret = os.environ.get(env_var, default)
        if ret is None and default is not None:
            return default
        elif ret is None:
            raise ValueError(f'Unable to find {env_var} in environment')
        if key.endswith('file'):
            val = Path(ret).resolve().read_text(encoding='utf-8')
            ret = val.splitlines()[0].split()[0]
        return ret

    def get_env_int(self, section: str, key: str, default: Optional[int] = None) -> int:
        try:
            ret = self.get_env(section, key)
        except ValueError:
            if default is None:
                raise
            return default
        try:
            return int(ret)
        except ValueError:
            raise ValueError(f'Unable to interpret {ret} as integer') from ValueError


GLOBALS = _Cached()


def to_datetime(value: Union[str, datetime], zone: Optional[str] = None) -> datetime:
    '''
    Parse a timestamp to datetime or ensure timezone is set. Since the database is likely to drop
    the timestamp, we will assume naive timestamps are intended to be UTC.
    '''
    if isinstance(value, datetime):
        ret = value
    else:
        ret = datetime.fromisoformat(value)
    if ret.tzinfo is None or ret.tzinfo.utcoffset(ret) is None:
        zoneinfo = pytz.timezone(zone) if zone is not None else pytz.utc
        ret = ret.replace(tzinfo=zoneinfo)
    return ret


def picture_timestamp(img_data: bytes, allow_naive: bool = False) -> Optional[datetime]:
    img = PIL.Image.open(io.BytesIO(img_data))
    exifdata = img.getexif()
    for tag_id in exifdata:
        tag = PIL.ExifTags.TAGS.get(tag_id, tag_id)
        if tag == 'DateTime':
            data = exifdata.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            if data:
                data = EXIF_TIME_PAT.sub(r'\1-\2-\3', data)
            return ((datetime.fromisoformat(data) if allow_naive else to_datetime(data))
                    if data else None)
    return None


def picture_format(img_data: bytes) -> Optional[str]:
    img = PIL.Image.open(io.BytesIO(img_data))
    return img.format


def strict_schema(schema: Dict[str, Any]):
    ''' Strictly check payload to ensure unknown keys are not provided. '''
    data = flask.request.json
    if data is None:
        raise werkzeug.exceptions.BadRequest('Must provide a JSON payload')
    accepted = list(schema['properties'].keys())
    for key in data.keys():
        if key not in accepted:
            raise werkzeug.exceptions.BadRequest(f'Unknown key "{key}" in payload')
