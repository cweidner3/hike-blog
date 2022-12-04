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

    def __init__(self) -> None:
        self._log_init = False

    @property
    def logger(self) -> logging.Logger:
        ''' Get a logger instance. '''
        log = flask.logging.create_logger(flask.current_app)
        return log


GLOBALS = _Cached()


def to_datetime(value: Union[str, datetime]) -> datetime:
    '''
    Parse a timestamp to datetime or ensure timezone is set. Since the database is likely to drop
    the timestamp, we will assume naive timestamps are intended to be UTC.
    '''
    if isinstance(value, datetime):
        ret = value
    else:
        ret = datetime.fromisoformat(value)
    if ret.tzinfo is None or ret.tzinfo.utcoffset(ret) is None:
        ret = ret.replace(tzinfo=pytz.utc)
    return ret


def picture_timestamp(img_data: bytes) -> Optional[datetime]:
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
            return to_datetime(data) if data else None
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
