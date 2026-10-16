from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class  Cirugia(Base):
    __tablename__ = "cirugias"

    id = Column(Integer, primary_key=True, index=True)
    nombrePaciente = Column(String(255), nullable=False)
    codigoPaciente = Column(String(255), nullable=False)
    fechaCirugia = Column(DateTime, nullable=False, index=True)
    procedimiento = Column(String(255), nullable=False)
    fechaDeRegistro = Column(DateTime, default=func.now(), nullable=False)
    duracionEstimada = Column(Integer, nullable=False)
    cirujano = Column(String(150), nullable=False)
    estatus = Column(String(30), nullable=False, default="PROGRAMADA")
    quirofano = Column(String(50), nullable=False)
    aseguradora = Column(String(255), nullable=True, default="Sin aseguradora")