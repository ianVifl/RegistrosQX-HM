from sqlalchemy import Column, DateTime, Index, Integer, String, Text, func

from app.database import Base


class Cirugia(Base):
    __tablename__ = "cirugias"
    __table_args__ = (
        Index("idx_fecha_cirugia", "fechaCirugia"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

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
