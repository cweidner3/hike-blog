"""Create pictures table

Revision ID: 23eb5ff46b3b
Revises: 4aa456f4567a
Create Date: 2022-11-27 22:18:00.532931

"""
from alembic import op
from sqlalchemy import Column, Text, LargeBinary, Integer, ForeignKey

from src.db.custom import AwareDateTime


# revision identifiers, used by Alembic.
revision = '23eb5ff46b3b'
down_revision = '4aa456f4567a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pictures',
        Column('id', Integer, primary_key=True),
        Column('parent', Integer, ForeignKey('hikes.id', ondelete='CASCADE'), nullable=False),
        Column('name', Text, nullable=False),
        Column('fmt', Text, nullable=False),
        Column('time', AwareDateTime, nullable=False),
        Column('data', LargeBinary, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('pictures')
