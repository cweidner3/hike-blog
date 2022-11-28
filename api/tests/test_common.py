# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

from datetime import datetime
from pathlib import Path
import unittest

import pytz

from tests.common import TESTS_FOLDER
from src.common import to_datetime, picture_timestamp, picture_format


class TestCommon(unittest.TestCase):
    def test_get_image_timestamp(self):
        img_file = Path(TESTS_FOLDER, 'test_data/2022-05-07 10.38.57.jpg')
        ts_ = picture_timestamp(img_file.read_bytes())
        self.assertIsNotNone(ts_)
        self.assertEqual(ts_, to_datetime('2022-05-07T10:38:57'))

    def test_get_image_no_timestamp(self):
        img_file = Path(TESTS_FOLDER, 'test_data/c0f89c4.png')
        ts_ = picture_timestamp(img_file.read_bytes())
        self.assertIsNone(ts_)

    def test_get_image_formats(self):
        data = [
            (Path(TESTS_FOLDER, 'test_data/2022-05-07 10.38.57.jpg'), 'JPEG'),
            (Path(TESTS_FOLDER, 'test_data/c0f89c4.png'), 'PNG'),
        ]
        for value, expect in data:
            with self.subTest(value=value.name):
                self.assertEqual(picture_format(value.read_bytes()), expect)

    def test_to_datetime(self):
        data = [
            ('2022-11-10T10:10:10Z', datetime(2022, 11, 10, 10, 10, 10, tzinfo=pytz.utc)),
            ('2022-11-10T10:10:10', datetime(2022, 11, 10, 10, 10, 10, tzinfo=pytz.utc)),
            (
                datetime(2022, 11, 10, 10, 10, 10),
                datetime(2022, 11, 10, 10, 10, 10, tzinfo=pytz.utc)
            ),
            (
                datetime(2022, 11, 10, 10, 10, 10, tzinfo=pytz.FixedOffset(-1 * 5 * 60)),
                datetime.fromisoformat('2022-11-10T10:10:10-0500')
            ),
        ]
        for value, expect in data:
            with self.subTest(value=value):
                self.assertEqual(to_datetime(value), expect)
