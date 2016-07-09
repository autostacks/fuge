# -*- encoding: utf-8 -*-
"""initial_fuge

Revision ID: 52dbd779c70f
Revises:
Create Date: 2016-07-04 19:08:37.305897

"""

# revision identifiers, used by Alembic.
revision = '52dbd779c70f'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('deleted', sa.Integer),
        sa.Column('report_count', sa.Integer(), nullable=False),
        sa.Column('host', sa.String(length=255)),
        sa.Column('binary', sa.String(length=255)),
        sa.Column('disabled', sa.Boolean()),
        sa.Column('disabled_reason', sa.String(length=255)),
        sa.Column('last_seen_up', sa.DateTime()),
        sa.Column('forced_down', sa.Boolean()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('host', 'binary',
                            name='uniq_services0host0binary')
    )