"""Create gpx data tables

Revision ID: 4aa456f4567a
Revises: cb9b785f35b6
Create Date: 2022-11-27 16:12:05.928490

"""
from alembic import op
from sqlalchemy import Column, Float, ForeignKey, Integer, Text, DateTime


# revision identifiers, used by Alembic.
revision = '4aa456f4567a'
down_revision = 'cb9b785f35b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tracks',
        Column('id', Integer, primary_key=True),
        Column('parent', Integer, ForeignKey('hikes.id', ondelete='CASCADE'), nullable=False),
        Column('name', Text),
        Column('description', Text),
    )
    op.create_table(
        'tracksegments',
        Column('id', Integer, primary_key=True),
        Column('parent', Integer, ForeignKey('tracks.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_table(
        'trackdata',
        Column('id', Integer, primary_key=True),
        Column('segment', Integer, ForeignKey('tracksegments.id', ondelete='CASCADE'), nullable=False),
        Column('time', DateTime),
        Column('latitude', Float),
        Column('longitude', Float),
        Column('elevation', Float),
    )
    op.create_table(
        'waypoints',
        Column('id', Integer, primary_key=True),
        Column('parent', Integer, ForeignKey('hikes.id', ondelete='CASCADE'), nullable=False),
        Column('name', Text),
        Column('description', Text),
        Column('time', AwareDateTime),
        Column('latitude', Float),
        Column('longitude', Float),
        Column('elevation', Float),
    )


def downgrade() -> None:
    op.drop_table('waypoints')
    op.drop_table('trackdata')
    op.drop_table('tracksegments')
    op.drop_table('tracks')
