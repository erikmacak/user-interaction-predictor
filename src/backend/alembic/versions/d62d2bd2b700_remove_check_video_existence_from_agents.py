"""remove check_video_existence from agents

Revision ID: d62d2bd2b700
Revises: 15ce7f78bdff
Create Date: 2026-03-15 14:54:31.845400

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd62d2bd2b700'
down_revision: Union[str, Sequence[str], None] = '15ce7f78bdff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.drop_column('agents', 'check_video_existence')

def downgrade() -> None:
    op.add_column('agents', sa.Column('check_video_existence', sa.Boolean(), nullable=False, server_default='true'))
