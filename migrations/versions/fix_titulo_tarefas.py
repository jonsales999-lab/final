"""Força a criação da coluna 'titulo' na tabela 'tarefas'

Revision ID: fix_titulo_tarefas
Revises: 62476d8dcd34
Create Date: 2026-01-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fix_titulo_tarefas'
down_revision: Union[str, Sequence[str], None] = '62476d8dcd34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Só adiciona a coluna se não existir
    conn = op.get_bind()
    result = conn.execute("SHOW COLUMNS FROM tarefas LIKE 'titulo'")
    if result.fetchone() is None:
        op.add_column('tarefas', sa.Column('titulo', sa.String(length=255), nullable=False, server_default=''))
        op.alter_column('tarefas', 'titulo', server_default=None)

def downgrade() -> None:
    op.drop_column('tarefas', 'titulo')
