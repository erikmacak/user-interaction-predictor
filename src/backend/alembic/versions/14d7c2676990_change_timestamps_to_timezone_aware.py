"""change timestamps to timezone aware

Revision ID: 14d7c2676990
Revises: 241274ac7e70
Create Date: 2026-02-22 14:57:09.620388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '14d7c2676990'
down_revision: Union[str, Sequence[str], None] = '241274ac7e70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE users ALTER COLUMN password_changed_at TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE users ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE')


def downgrade() -> None:
    op.execute('ALTER TABLE users ALTER COLUMN password_changed_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE users ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE')