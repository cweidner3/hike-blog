'''
Database setup and engine provider.
'''

from datetime import datetime
import os
from typing import Dict, Optional

import flask
import sqlalchemy
import sqlalchemy.orm

from src.db.base import Base
from src.db.custom import AwareDateTime


def _get_db_uri(env: Optional[Dict[str, str]] = None):
    _env = os.environ if env is None else env
    dialect = _env.get('DB_DIALECT', 'postgres')
    uname = _env.get('DB_USER', '')
    passwd = _env.get('DB_PASS', '')
    host = _env.get('DB_HOST', '')
    name = _env.get('DB_NAME', '')
    creds = f'{uname}:{passwd}' if passwd else uname
    login = f'{creds}@' if creds else ''
    if dialect == 'mariadb':
        return f'mysql+pymysql://{login}{host}/{name}'
    return f'postgresql://{login}{host}/{name}'


def get_db_uri(env: Optional[Dict[str, str]] = None):
    return _get_db_uri(env)


class JsonSerializer(flask.json.JSONEncoder):
    def default(self, o):
        def _nested(data):
            if isinstance(data, Base):
                maybe = getattr(data, 'serialized')
                if maybe:
                    return maybe
                it_ = data._sa_class_manager.keys()  # pylint: disable=protected-access
                it_ = map(lambda x: (f'{x}', _nested(getattr(data, x))), it_)
                return dict(it_)
            if isinstance(data, datetime):
                return data.isoformat()
            if isinstance(data, AwareDateTime):
                return data.timestamp.isoformat() if data.timestamp is not None else None
            if isinstance(data, dict):
                it_ = data.items()
                it_ = map(lambda x: (x[0], _nested(x[1])), it_)
                return dict(it_)
            if isinstance(data, list):
                return list(map(_nested, data))
            return flask.json.JSONEncoder.default(self, data)

        return _nested(o)


engine = sqlalchemy.create_engine(_get_db_uri(), echo=True)
