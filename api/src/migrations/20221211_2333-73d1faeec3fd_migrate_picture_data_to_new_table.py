"""Migrate picture data to new table

Revision ID: 73d1faeec3fd
Revises: 0ee2ef5c2e29
Create Date: 2022-12-11 23:33:15.587847

"""
from alembic import op
from sqlalchemy import Column, LargeBinary


# revision identifiers, used by Alembic.
revision = '73d1faeec3fd'
down_revision = '0ee2ef5c2e29'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('pictures', 'data')


def downgrade() -> None:
    op.add_column('pictures', Column('data', LargeBinary(1 << 24), nullable=False))
