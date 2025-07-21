from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# Identificadores da migração (gerados automaticamente pelo flask db migrate)
revision = 'xxxx'
down_revision = 'yyyy'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tb_users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade():
    op.drop_column('tb_users', 'is_admin')
