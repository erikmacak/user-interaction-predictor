"""allow null agent_id in audit_sessions

Revision ID: 15ce7f78bdff
Revises: ac79b66b3a90
Create Date: 2026-03-14 15:41:06.866016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '15ce7f78bdff'
down_revision: Union[str, Sequence[str], None] = 'ac79b66b3a90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column('audit_sessions', 'agent_id',
               existing_type=sa.UUID(),
               nullable=True)

def downgrade() -> None:
    op.alter_column('audit_sessions', 'agent_id',
               existing_type=sa.UUID(),
               nullable=False)