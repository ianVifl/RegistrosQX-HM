from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class EstatusCirugia(str, Enum):
    PROGRAMADA = "PROGRAMADA"
    EN_PROGRESO = "EN PROGRESO"
    FINALIZADA = "FINALIZADA"


class CirugiaBase(BaseModel):
    nombrePaciente: str = Field(min_length=1, max_length=255)
    codigoPaciente: str = Field(min_length=1, max_length=255)
    fechaCirugia: datetime
    procedimiento: str = Field(min_length=1, max_length=255)
    duracionEstimada: int = Field(gt=0, le=720, multiple_of=30)
    cirujano: str = Field(min_length=1, max_length=150)
    quirofano: str = Field(min_length=1, max_length=50)
    aseguradora: str | None = Field(default="No", max_length=255)

    @field_validator(
        "nombrePaciente", "codigoPaciente", "procedimiento",
        "cirujano", "quirofano", "aseguradora",
        mode="before",
    )
    @classmethod
    def limpiar_espacios(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("aseguradora", mode="after")
    @classmethod
    def aseguradora_por_defecto(cls, v):
        return v or "No"


class CirugiaCreate(CirugiaBase):
    pass


class CirugiaUpdate(CirugiaBase):
    estatus: EstatusCirugia
    model_config = ConfigDict(use_enum_values=True)


class EstatusUpdate(BaseModel):
    estatus: EstatusCirugia
    model_config = ConfigDict(use_enum_values=True)


class CirugiaOut(BaseModel):
    id: int
    nombrePaciente: str | None = None
    codigoPaciente: str
    fechaCirugia: datetime
    procedimiento: str
    duracionEstimada: int
    cirujano: str
    estatus: str
    quirofano: str
    aseguradora: str | None = "No"
    fechaDeRegistro: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("aseguradora", mode="after")
    @classmethod
    def aseguradora_por_defecto(cls, v):
        return v or "No"

    @computed_field
    @property
    def fechaFinEstimada(self) -> datetime:
        return self.fechaCirugia + timedelta(minutes=self.duracionEstimada)
