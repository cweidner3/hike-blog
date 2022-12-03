#!/usr/bin/env python3

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz
import requests
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.db.models import Hike
from tests.common import engine, get_logger, query_route

LOG = get_logger()

HERE = Path(__file__).parent.resolve()
_TIMEOUT = 10


def _ts_w_tz(date_time: str, timezone: str) -> str:
    val = datetime.fromisoformat(date_time)
    tzinfo = pytz.timezone(timezone)
    val = val.replace(tzinfo=tzinfo)
    return val.astimezone(pytz.utc).isoformat()


HIKE = {
    'name': 'my-test-hike',
    'start': _ts_w_tz('2022-05-07 10:00:00', 'America/New_York'),
    'end': _ts_w_tz('2022-05-09 14:00:00', 'America/New_York'),
}

TRACKS = list(Path(HERE, 'hike_data').glob('*.gpx'))

PICTURES = list(Path(HERE, 'hike_data').glob('*.jpg'))


def _replace() -> bool:
    value = os.environ.get('REPLACE', '0')
    return int(value) > 0


def _hike_exists() -> Optional[int]:
    with Session(engine) as session:
        ret = session.execute(
            select(Hike.id, Hike.name)
            .where(Hike.name == HIKE['name'])
        ).one_or_none()
        return ret[0] if ret is not None else None


def _remove_previous_hike():
    LOG.info('Removing any existing hikes with name "%s"', HIKE['name'])
    with Session(engine) as session:
        session.execute(
            delete(Hike)
            .where(Hike.name == HIKE['name'])
        )
        session.commit()


def _create_new_hike() -> int:
    LOG.info('Creating new hike with %s...', HIKE)
    resp = requests.post(
        query_route('api', '/hikes/new'),
        json=HIKE,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data['id']


def _update_hike(hike_id: int) -> int:
    pass


def _upload_tracks(hike_id: int):
    for file in TRACKS:
        LOG.info('Uploading gpx file %s...', file)
        with open(file, 'rb') as inf:
            resp = requests.post(
                query_route('api', f'/hikes/{hike_id}/data'),
                files={file.name: inf},
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()


def _upload_pictures(hike_id: int):
    for file in PICTURES:
        LOG.info('Uploading picture %s...', file)
        with open(file, 'rb') as inf:
            resp = requests.post(
                query_route('api', f'/pictures/hike/{hike_id}'),
                files={file.name: inf},
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()


def _main():
    hike_id = None if _replace() else _hike_exists()
    if hike_id is None:
        if _replace():
            _remove_previous_hike()
        hike_id = _create_new_hike()
    else:
        _update_hike(hike_id)
    _upload_tracks(hike_id)
    _upload_pictures(hike_id)

    LOG.info('DONE')


if __name__ == '__main__':
    _main()
