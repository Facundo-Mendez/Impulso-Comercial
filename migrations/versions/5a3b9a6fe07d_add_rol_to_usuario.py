"""add rol to usuario

Revision ID: 5a3b9a6fe07d
Revises: 8949c569ae22
Create Date: 2025-08-30 17:43:37.197931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a3b9a6fe07d'
down_revision = '8949c569ae22'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Agregamos columna con un valor por defecto ("usuario") para que SQLite lo acepte
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('rol', sa.String(length=20), nullable=False, server_default='usuario')
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.drop_column('rol')


    # ### end Alembic commands ###
