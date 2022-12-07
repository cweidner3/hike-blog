"""Create Hike Table

Revision ID: cb9b785f35b6
Revises:
Create Date: 2022-11-26 12:40:17.002975

"""
from alembic import op
from sqlalchemy import Column, Date, Integer, Text


# revision identifiers, used by Alembic.
revision = 'cb9b785f35b6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'hikes',
        Column('id', Integer, primary_key=True),
        Column('name', Text, nullable=False),
        Column('start', Date),
        Column('end', Date),
    )


def downgrade() -> None:
    op.drop_table('hikes')
