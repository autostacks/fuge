"""create_containers_table

Revision ID: 1086176424fd
Revises: 52dbd779c70f
Create Date: 2016-07-09 07:04:19.316772

"""

# revision identifiers, used by Alembic.
revision = '1086176424fd'
down_revision = '52dbd779c70f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'containers',
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('deleted_at', sa.DateTime()),
        sa.Column('deleted', sa.Integer()),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(length=255)),
        sa.Column('user_id', sa.String(length=255)),
        sa.Column('uuid', sa.String(length=36)),
        sa.Column('name', sa.String(length=255)),
        sa.Column('image', sa.String(length=255)),
        sa.Column('command', sa.String(length=255)),
        sa.Column('status', sa.String(length=20)),
        sa.Column('memory', sa.String(length=255)),
        sa.Column('environment', sa.Text()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid', name='uniq_containers0uuid'))
