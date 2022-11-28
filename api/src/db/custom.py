'''
Custom data types for the ORM.
'''

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, TypeDecorator

from src.common import to_datetime


class AwareDateTime(TypeDecorator):
    ''' Returns an aware datetime such that timezone is assumed to be UTC. '''
    impl = DateTime

    def process_result_value(self, value: Optional[datetime], dialect):
        if value:
            return to_datetime(value)
        return value
