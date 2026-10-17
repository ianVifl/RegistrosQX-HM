"""usuarios, bitacora y auditoria

Revision ID: c99e125e9075
Revises: 8b1f5d68ae04
Create Date: 2026-10-17 13:23:29.915859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c99e125e9075'
down_revision: Union[str, Sequence[str], None] = '8b1f5d68ae04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Usuarios con rol, bitácora de movimientos y columnas de auditoría en cirugias."""
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario', sa.String(length=50), nullable=False),
    sa.Column('nombre', sa.String(length=150), nullable=False),
    sa.Column('passwordHash', sa.String(length=255), nullable=False),
    sa.Column('rol', sa.String(length=20), nullable=False),
    sa.Column('activo', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('creadoEn', sa.DateTime(), nullable=False),
    sa.Column('actualizadoEn', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usuario', name='uq_usuarios_usuario'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_table('bitacora',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('usuarioId', sa.Integer(), nullable=True),
    sa.Column('usuarioNombre', sa.String(length=150), nullable=False),
    sa.Column('usuarioRol', sa.String(length=20), nullable=False),
    sa.Column('accion', sa.String(length=30), nullable=False),
    sa.Column('entidad', sa.String(length=30), nullable=False),
    sa.Column('entidadId', sa.Integer(), nullable=True),
    sa.Column('detalle', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['usuarioId'], ['usuarios.id'], name='fk_bitacora_usuario'),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('idx_bitacora_fecha', 'bitacora', ['fecha'], unique=False)
    op.add_column('cirugias', sa.Column('creadoPorId', sa.Integer(), nullable=True))
    op.add_column('cirugias', sa.Column('actualizadoPorId', sa.Integer(), nullable=True))
    op.add_column('cirugias', sa.Column('actualizadoEn', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_cirugias_creado_por', 'cirugias', 'usuarios', ['creadoPorId'], ['id'])
    op.create_foreign_key('fk_cirugias_actualizado_por', 'cirugias', 'usuarios', ['actualizadoPorId'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_cirugias_actualizado_por', 'cirugias', type_='foreignkey')
    op.drop_constraint('fk_cirugias_creado_por', 'cirugias', type_='foreignkey')
    op.drop_column('cirugias', 'actualizadoEn')
    op.drop_column('cirugias', 'actualizadoPorId')
    op.drop_column('cirugias', 'creadoPorId')
    op.drop_index('idx_bitacora_fecha', table_name='bitacora')
    op.drop_table('bitacora')
    op.drop_table('usuarios')
