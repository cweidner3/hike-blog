"""Add timezone column to tables with aware timestamps

Revision ID: 991b63134bdc
Revises: b05fb445684f
Create Date: 2022-12-04 08:00:49.236126

"""
from alembic import op
import pytz
from sqlalchemy import Column, Date, DateTime, Text, ForeignKey


# revision identifiers, used by Alembic.
revision = '991b63134bdc'
down_revision = 'b05fb445684f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    tztable = op.create_table(
        'timezones',
        Column('name', Text, index=True, primary_key=True),
    )
    assert tztable is not None
    op.bulk_insert(tztable, list(map(lambda x: dict(name=x), pytz.common_timezones)))

    op.add_column('hikes', Column('zone', Text, ForeignKey('timezones.name'), server_default='UTC'))
    op.execute("UPDATE hikes SET zone = 'UTC'")
    op.alter_column('hikes', 'zone', nullable=False)
    op.alter_column('hikes', 'start', type_=DateTime)
    op.alter_column('hikes', 'end', type_=DateTime)


def downgrade() -> None:
    op.drop_column('hikes', 'zone')
    op.alter_column('hikes', 'start', type_=Date)
    op.alter_column('hikes', 'end', type_=Date)
    op.drop_table('timezones')
