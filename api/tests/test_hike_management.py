# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import unittest
from sqlalchemy import delete

from sqlalchemy.orm import Session
import requests

from tests.common import engine, get_logger, query_route
from src.db.models import Hike

_TIMEOUT = 10

LOG = get_logger()


class TestHikeManagement(unittest.TestCase):
    PL_GOOD = {'name': 'test-hike-1', 'start': '2022-11-22T10:00:00-05:00'}

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
