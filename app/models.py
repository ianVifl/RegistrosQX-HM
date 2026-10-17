from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, true

from app.database import Base

UTF8 = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}


class Cirugia(Base):
    __tablename__ = "cirugias"
    __table_args__ = (Index("idx_fecha_cirugia", "fechaCirugia"), UTF8)

    id = Column(Integer, primary_key=True, index=True)
    nombrePaciente = Column(String(255), nullable=False)
    edad = Column(Integer, nullable=False)
    sexo = Column(String(10), nullable=False)
    fechaCirugia = Column(DateTime, nullable=False)
    procedimiento = Column(String(255), nullable=False)
    fechaDeRegistro = Column(DateTime, default=func.now(), nullable=False)
    duracionEstimada = Column(Integer, nullable=False)
    cirujano = Column(String(150), nullable=False)
    estatus = Column(String(30), nullable=False, default="PROGRAMADA", server_default="PROGRAMADA")
    quirofano = Column(String(50), nullable=False)
    aseguradora = Column(String(255), nullable=True, default="Sin aseguradora")
    serviciosEspeciales = Column(Text, nullable=True)
    diagnostico = Column(Text, nullable=True)
    creadoPorId = Column(Integer, ForeignKey("usuarios.id", name="fk_cirugias_creado_por"), nullable=True)
    actualizadoPorId = Column(Integer, ForeignKey("usuarios.id", name="fk_cirugias_actualizado_por"), nullable=True)
    actualizadoEn = Column(DateTime, nullable=True)


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (UniqueConstraint("usuario", name="uq_usuarios_usuario"), UTF8)

    id = Column(Integer, primary_key=True)
    usuario = Column(String(50), nullable=False)
    nombre = Column(String(150), nullable=False)
    passwordHash = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False)
    activo = Column(Boolean, nullable=False, default=True, server_default=true())
    creadoEn = Column(DateTime, nullable=False)
    actualizadoEn = Column(DateTime, nullable=False)


class Bitacora(Base):
    __tablename__ = "bitacora"
    __table_args__ = (Index("idx_bitacora_fecha", "fecha"), UTF8)

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=False)
    usuarioId = Column(Integer, ForeignKey("usuarios.id", name="fk_bitacora_usuario"), nullable=True)  # NULL = sistema (scheduler)
    usuarioNombre = Column(String(150), nullable=False)
    usuarioRol = Column(String(20), nullable=False)
    accion = Column(String(30), nullable=False)
    entidad = Column(String(30), nullable=False)
    entidadId = Column(Integer, nullable=True)
    detalle = Column(JSON, nullable=True)
