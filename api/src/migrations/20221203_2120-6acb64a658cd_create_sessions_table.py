"""Create sessions table

Revision ID: 6acb64a658cd
Revises: 23eb5ff46b3b
Create Date: 2022-12-03 21:20:08.722869

"""
from alembic import op
from sqlalchemy import Boolean, Column, Integer, Text, String
import uuid


# revision identifiers, used by Alembic.
revision = '6acb64a658cd'
down_revision = '23eb5ff46b3b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = op.create_table(
        'session',
        Column('id', Integer, primary_key=True),
        Column('key', String(256), unique=True, nullable=False),
        Column('username', Text, nullable=False),
        Column('displayname', Text, nullable=False),
        Column('admin', Boolean, default=False),
    )
    assert table is not None
    op.bulk_insert(table, [
        dict(id=1, key=str(uuid.uuid4()), username='cora', displayname='Cora', admin=True),
    ])


def downgrade() -> None:
    op.drop_table('session')
