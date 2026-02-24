"""create agents table

Revision ID: 9d97b6a28f35
Revises: 241274ac7e70
Create Date: 2026-02-23 18:49:40.268830

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9d97b6a28f35'
down_revision: Union[str, Sequence[str], None] = '14d7c2676990'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'agents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('predictor_version', sa.String(length=50), nullable=False),
        sa.Column('check_video_existence', sa.Boolean(), nullable=False),
        sa.Column('state_file_data', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_name'), 'agents', ['name'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_agents_name'), table_name='agents')
    op.drop_table('agents')