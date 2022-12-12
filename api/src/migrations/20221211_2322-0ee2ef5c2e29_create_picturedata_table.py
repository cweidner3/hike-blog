"""Create picturedata table

Revision ID: 0ee2ef5c2e29
Revises: 692e53a878cb
Create Date: 2022-12-11 23:22:42.781795

"""
from alembic import op
from sqlalchemy import Column, Integer, ForeignKey, LargeBinary, String


# revision identifiers, used by Alembic.
revision = '0ee2ef5c2e29'
down_revision = '692e53a878cb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'picturedata',
        Column('id', Integer, primary_key=True),
        Column('parent', Integer, ForeignKey('pictures.id', ondelete='CASCADE'), nullable=False),
        Column('size', Integer, nullable=False),
        Column('resized', String(32), nullable=False),
        Column('sha', String(256), nullable=False),
        Column('data', LargeBinary(1 << 24), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('picturedata')
