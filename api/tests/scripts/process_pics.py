#!/usr/bin/env python3

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz
import requests
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.db.models import Hike, ApiSession
from tests.common import engine, get_logger, query_route

LOG = get_logger()

HERE = Path(__file__).parent.resolve()
_TIMEOUT = 10



def _api_session_key() -> str:
    with Session(engine) as session:
        ret = session.execute(
            select(ApiSession.key, ApiSession.admin)
            .where(ApiSession.admin == True)
            .limit(1)
        ).all()
        assert len(ret) > 0
        return ret[0][0]


def _main():
    headers = {
        'Api-Session': _api_session_key(),
    }
    url = query_route('api', '/pictures/process', query={'limit': 5})
    resp = requests.post(
        url,
        headers=headers,
        timeout=60,
    )
    resp.raise_for_status()

    LOG.info('%s', resp.json())


_main()
