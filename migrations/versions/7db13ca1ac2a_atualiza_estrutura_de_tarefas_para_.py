"""Atualiza estrutura de tarefas para materiais/unidades

Revision ID: 7db13ca1ac2a
Revises: a334545fe236
Create Date: 2026-01-19 16:31:44.099705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7db13ca1ac2a'
down_revision: Union[str, Sequence[str], None] = 'a334545fe236'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
