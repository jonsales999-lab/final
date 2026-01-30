"""Adiciona colunas novas em tarefas

Revision ID: 62476d8dcd34
Revises: 7db13ca1ac2a
Create Date: 2026-01-19 16:33:21.439280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62476d8dcd34'
down_revision: Union[str, Sequence[str], None] = '7db13ca1ac2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tarefas', sa.Column('titulo', sa.String(length=255), nullable=False))
    op.add_column('tarefas', sa.Column('pontuacao', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('tarefas', sa.Column('unidade_id', sa.Integer(), nullable=True))
    op.add_column('tarefas', sa.Column('material_id', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tarefas', 'material_id')
    op.drop_column('tarefas', 'unidade_id')
    op.drop_column('tarefas', 'pontuacao')
    op.drop_column('tarefas', 'titulo')
