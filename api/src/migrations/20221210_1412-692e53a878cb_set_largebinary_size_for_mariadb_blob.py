"""Set LargeBinary size for MariaDB BLOB

Revision ID: 692e53a878cb
Revises: 991b63134bdc
Create Date: 2022-12-10 14:12:58.313588

"""
from alembic import op
from sqlalchemy import LargeBinary


# revision identifiers, used by Alembic.
revision = '692e53a878cb'
down_revision = '991b63134bdc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('pictures', 'data', type_=LargeBinary(1 << 24))


def downgrade() -> None:
    op.alter_column('pictures', 'data', type_=LargeBinary)
