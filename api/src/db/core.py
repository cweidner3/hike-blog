'''
Database setup and engine provider.
'''

import os
import flask
from typing import Dict, Optional

import sqlalchemy
import sqlalchemy.orm

from src.db.base import Base


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


class JsonSerializer(flask.json.JSONEncoder):
    def default(self, obj):
        def _nested(data):
            if isinstance(data, Base):
                maybe = getattr(data, 'serialized')
                if maybe:
                    return maybe
                it_ = data._sa_class_manager.keys()
                it_ = map(lambda x: (f'{x}', _nested(getattr(data, x))), it_)
                return dict(it_)
            elif isinstance(data, dict):
                it_ = data.items()
                it_ = map(lambda x: (x[0], _nested(x[1])), it_)
                return dict(it_)
            elif isinstance(data, list):
                return list(map(_nested, data))
            else:
                return data

        return _nested(obj)


engine = sqlalchemy.create_engine(_get_db_uri())
