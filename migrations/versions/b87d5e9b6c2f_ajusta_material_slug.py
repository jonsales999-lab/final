"""Ajusta material para slug e alinha FK de tarefas

Revision ID: b87d5e9b6c2f
Revises: fix_titulo_tarefas
Create Date: 2026-01-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b87d5e9b6c2f"
down_revision: Union[str, Sequence[str], None] = "fix_titulo_tarefas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Muda material.id e tarefas.material_id para VARCHAR(100) e remove tipo se existir."""
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Remove FKs existentes de tarefas -> material (nome pode variar)
    for fk in insp.get_foreign_keys("tarefas"):
        if fk.get("referred_table") == "material":
            op.drop_constraint(fk["name"], "tarefas", type_="foreignkey")

    # Remove coluna tipo se ainda existir
    tarefa_cols = [c["name"] for c in insp.get_columns("tarefas")]
    if "tipo" in tarefa_cols:
        op.drop_column("tarefas", "tipo")

    # Altera PK de material para string (slug)
    op.alter_column(
        "material",
        "id",
        existing_type=sa.Integer(),
        type_=sa.String(length=100),
        existing_nullable=False,
    )

    # Altera FK em tarefas para string
    op.alter_column(
        "tarefas",
        "material_id",
        existing_type=sa.Integer(),
        type_=sa.String(length=100),
        existing_nullable=True,
    )

    # Recria FK
    op.create_foreign_key(
        "fk_tarefas_material_id_material",
        "tarefas",
        "material",
        ["material_id"],
        ["id"],
    )



def downgrade() -> None:
    """Reverte tipos para Integer e recria FK; reintroduz coluna tipo."""
    # Remove FK atual
    op.drop_constraint(
        "fk_tarefas_material_id_material",
        "tarefas",
        type_="foreignkey",
    )

    # Reverte tipos
    op.alter_column(
        "tarefas",
        "material_id",
        existing_type=sa.String(length=100),
        type_=sa.Integer(),
        existing_nullable=True,
    )

    op.alter_column(
        "material",
        "id",
        existing_type=sa.String(length=100),
        type_=sa.Integer(),
        existing_nullable=False,
    )

    # Recria FK
    op.create_foreign_key(
        "fk_tarefas_material_id_material",
        "tarefas",
        "material",
        ["material_id"],
        ["id"],
    )

    # Recria coluna tipo (sem default)
    op.add_column("tarefas", sa.Column("tipo", sa.String(length=50), nullable=True))
