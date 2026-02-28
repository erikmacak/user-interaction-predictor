"""create audit sessions table

Revision ID: 5e9cc3ded3fc
Revises: 9d97b6a28f35
Create Date: 2026-02-24 22:06:27.347678

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '5e9cc3ded3fc'
down_revision: Union[str, Sequence[str], None] = '9d97b6a28f35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'audit_sessions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_sessions_agent_id'), 'audit_sessions', ['agent_id'])
    op.create_index(op.f('ix_audit_sessions_state'), 'audit_sessions', ['state'])

def downgrade() -> None:
    op.drop_index(op.f('ix_audit_sessions_state'), table_name='audit_sessions')
    op.drop_index(op.f('ix_audit_sessions_agent_id'), table_name='audit_sessions')
    op.drop_table('audit_sessions')
