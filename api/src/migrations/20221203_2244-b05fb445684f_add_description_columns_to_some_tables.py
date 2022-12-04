"""Add description columns to some tables

Revision ID: b05fb445684f
Revises: 6acb64a658cd
Create Date: 2022-12-03 22:44:59.685318

"""
from alembic import op
from sqlalchemy import Column, Text


# revision identifiers, used by Alembic.
revision = 'b05fb445684f'
down_revision = '6acb64a658cd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('hikes', Column('title', Text))
    op.add_column('hikes', Column('brief', Text))
    op.add_column('hikes', Column('description', Text))
    op.add_column('pictures', Column('description', Text))


def downgrade() -> None:
    op.drop_column('hikes', 'title')
    op.drop_column('hikes', 'brief')
    op.drop_column('hikes', 'description')
    op.drop_column('pictures', 'description')
