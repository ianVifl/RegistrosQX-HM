"""datos clinicos del paciente

Revision ID: 8b1f5d68ae04
Revises: 8392ed4674d8
Create Date: 2026-10-17 12:34:12.263387

Quita codigoPaciente y agrega edad, sexo, serviciosEspeciales y diagnostico.
edad y sexo son NOT NULL sin default: la tabla debe estar vacía al aplicar esta migración.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '8b1f5d68ae04'
down_revision: Union[str, Sequence[str], None] = '8392ed4674d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('cirugias', sa.Column('edad', sa.Integer(), nullable=False))
    op.add_column('cirugias', sa.Column('sexo', sa.String(length=10), nullable=False))
    op.add_column('cirugias', sa.Column('serviciosEspeciales', sa.Text(), nullable=True))
    op.add_column('cirugias', sa.Column('diagnostico', sa.Text(), nullable=True))
    op.drop_column('cirugias', 'codigoPaciente')


def downgrade() -> None:
    # Los códigos borrados no se pueden recuperar: las filas existentes quedan con código vacío.
    op.add_column('cirugias', sa.Column('codigoPaciente', sa.String(length=255), nullable=False, server_default=''))
    op.alter_column('cirugias', 'codigoPaciente', server_default=None, existing_type=sa.String(length=255), existing_nullable=False)
    op.drop_column('cirugias', 'diagnostico')
    op.drop_column('cirugias', 'serviciosEspeciales')
    op.drop_column('cirugias', 'sexo')
    op.drop_column('cirugias', 'edad')
