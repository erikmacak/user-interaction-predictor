"""add_video_logs_table

Revision ID: ac79b66b3a90
Revises: 5e9cc3ded3fc
Create Date: 2026-03-03 21:12:48.056059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'ac79b66b3a90'
down_revision: Union[str, Sequence[str], None] = '5e9cc3ded3fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'video_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.UUID(), nullable=False),
        sa.Column('agent_id', sa.UUID(), nullable=False),
        sa.Column('video_url', sa.String(), nullable=False),
        sa.Column('video_id', sa.String(), nullable=False),
        sa.Column('video_author', sa.String(), nullable=True),
        sa.Column('video_description', sa.String(), nullable=True),
        sa.Column('video_time_duration', sa.Integer(), nullable=True),
        sa.Column('video_action_watch', sa.Boolean(), nullable=True),
        sa.Column('video_action_like', sa.Boolean(), nullable=True),
        sa.Column('video_action_bookmark', sa.Boolean(), nullable=True),
        sa.Column('user_email', sa.String(), nullable=True),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('country_code', sa.String(), nullable=True),
        sa.Column('date_of_birth', sa.String(), nullable=True),
        sa.Column('predicted_topic', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['audit_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_video_logs_session_id', 'video_logs', ['session_id'])
    op.create_index('ix_video_logs_agent_id', 'video_logs', ['agent_id'])


def downgrade() -> None:
    op.drop_index('ix_video_logs_agent_id', table_name='video_logs')
    op.drop_index('ix_video_logs_session_id', table_name='video_logs')
    
    op.drop_table('video_logs')
