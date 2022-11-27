# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from pathlib import Path
import unittest

import requests
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.db.models import Hike
from tests.common import DATA_FOLDER, engine, get_logger, query_route

_TIMEOUT = 10

LOG = get_logger()


class TestHikeManagement(unittest.TestCase):
    PL_GOOD = {'name': 'test-hike-1', 'start': '2022-11-22T10:00:00-05:00'}

    TEST_FILES = [
        Path(DATA_FOLDER, '20220507-CT-North-Chick-Hike/gpx-data/CT - North Chick - Day 1.gpx'),
        Path(
            DATA_FOLDER,
            '20220507-CT-North-Chick-Hike/gpx-data/CT - North Chick - Stevenson Branch Campsite.gpx'
        ),
    ]

    def setUp(self) -> None:
        with Session(engine) as session:
            session.execute(
                delete(Hike)
                .where(Hike.name == self.PL_GOOD['name'])
            )
            session.commit()
        return super().setUp()

    def test_create_delete(self):
        '''
        Assert the ability to create a new hike entry and that it can then be deleted using the
        returned hike id.
        '''
        data = self.PL_GOOD.copy()
        resp = requests.post(query_route('api', '/hikes/new'), json=data, timeout=_TIMEOUT)
        self.assertEqual(resp.status_code, 200)
        rdata = resp.json()
        self.assertIn('id', rdata)
        self.assertIn('name', rdata)
        self.assertIn('start', rdata)

        resp = requests.delete(query_route('api', f'/hikes/{rdata["id"]}'), timeout=_TIMEOUT)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'OK')

    def test_import_hike(self):
        data = self.PL_GOOD.copy()
        resp = requests.post(query_route('api', '/hikes/new'), json=data, timeout=_TIMEOUT)
        self.assertEqual(resp.status_code, 200)
        rdata = resp.json()

        it_ = self.TEST_FILES
        it_ = map(lambda x: (x.name, x.read_bytes()), it_)
        files = dict(it_)
        resp = requests.post(
            query_route('api', f'/hikes/{rdata["id"]}/data'),
            timeout=_TIMEOUT,
            files=files,
        )
        self.assertEqual(resp.status_code, 200)
