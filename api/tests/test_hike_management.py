# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from pathlib import Path
import unittest

import requests
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.db.models import Hike, Picture
from tests.common import DATA_FOLDER, TESTS_FOLDER, engine, get_logger, query_route

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


class TestHikeData(unittest.TestCase):

    PL_GOOD = {'name': 'test-hike-2', 'start': '2022-11-22T10:00:00-05:00'}

    def setUp(self) -> None:
        with Session(engine) as session:
            hike = session.execute(
                select(Hike.id, Hike.name)
                .where(Hike.name == self.PL_GOOD['name'])
            ).one_or_none()
            if hike is None:
                hike_o = Hike(
                    name=self.PL_GOOD['name'],
                    start=self.PL_GOOD['start'],
                )
                session.add(hike_o)
                session.flush()
                hike = session.execute(
                    select(Hike.id, Hike.name)
                    .where(Hike.name == self.PL_GOOD['name'])
                ).one()
            self._hike = hike
            session.commit()
        return super().setUp()

    def test_upload_pictures(self):
        files = [
            'test_data/2022-05-07 10.38.57.jpg',
            'test_data/c0f89c4.png',
        ]
        files = map(lambda x: Path(TESTS_FOLDER, x), files)
        files = list(files)
        with Session(engine) as session:
            session.execute(
                delete(Picture)
                .where(Picture.name in list(map(lambda x: x.name, files)))
            )
            session.commit()
        for file in files:
            with self.subTest(file=file):
                with open(file, 'rb') as inf:
                    resp = requests.post(
                        query_route('api', f'/pictures/hike/{self._hike[0]}'),
                        files={file.name: inf},
                        timeout=_TIMEOUT,
                    )
                    self.assertEqual(resp.status_code, 200)
                    self.assertIn('status', resp.json())
                    self.assertIn('created', resp.json())
                    self.assertEqual(resp.json()['status'], 'OK')
