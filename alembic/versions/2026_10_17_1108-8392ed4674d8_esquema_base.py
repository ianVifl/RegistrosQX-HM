"""esquema base

Revision ID: 8392ed4674d8
Revises: 
Create Date: 2026-10-17 11:08:34.579971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8392ed4674d8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Tabla `cirugias` tal como existía antes de usar Alembic.

    En una BD que ya tiene la tabla NO se ejecuta: se marca con `alembic stamp 8392ed4674d8`.
    Solo corre en una BD vacía (entorno nuevo, BD de tests).
    """
    op.create_table(
        "cirugias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nombrePaciente", sa.String(255), nullable=False),
        sa.Column("codigoPaciente", sa.String(255), nullable=False),
        sa.Column("fechaCirugia", sa.DateTime(), nullable=False),
        sa.Column("procedimiento", sa.String(255), nullable=False),
        sa.Column("fechaDeRegistro", sa.DateTime(), nullable=False),
        sa.Column("duracionEstimada", sa.Integer(), nullable=False),
        sa.Column("cirujano", sa.String(150), nullable=False),
        sa.Column("estatus", sa.String(30), nullable=False, server_default="PROGRAMADA"),
        sa.Column("quirofano", sa.String(50), nullable=False),
        sa.Column("aseguradora", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
    )
    op.create_index("ix_cirugias_id", "cirugias", ["id"])
    op.create_index("idx_fecha_cirugia", "cirugias", ["fechaCirugia"])


def downgrade() -> None:
    op.drop_table("cirugias")
