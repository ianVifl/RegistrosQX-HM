from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class EstatusCirugia(str, Enum):
    PROGRAMADA = "PROGRAMADA"
    EN_PROGRESO = "EN PROGRESO"
    FINALIZADA = "FINALIZADA"


class Sexo(str, Enum):
    FEMENINO = "FEMENINO"
    MASCULINO = "MASCULINO"


class CirugiaBase(BaseModel):
    nombrePaciente: str = Field(min_length=1, max_length=255)
    edad: int = Field(ge=0, le=120)
    sexo: Sexo
    fechaCirugia: datetime
    procedimiento: str = Field(min_length=1, max_length=255)
    duracionEstimada: int = Field(gt=0, le=720, multiple_of=30)
    cirujano: str = Field(min_length=1, max_length=150)
    quirofano: str = Field(min_length=1, max_length=50)
    aseguradora: str | None = Field(default="No", max_length=255)
    serviciosEspeciales: str | None = None
    diagnostico: str | None = None

    model_config = ConfigDict(use_enum_values=True)

    @field_validator(
        "nombrePaciente", "procedimiento", "cirujano", "quirofano",
        "aseguradora", "serviciosEspeciales", "diagnostico",
        mode="before",
    )
    @classmethod
    def limpiar_espacios(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("aseguradora", mode="after")
    @classmethod
    def aseguradora_por_defecto(cls, v):
        return v or "No"

    @field_validator("serviciosEspeciales", "diagnostico", mode="after")
    @classmethod
    def vacio_a_nulo(cls, v):
        return v or None


class CirugiaCreate(CirugiaBase):
    pass


class CirugiaUpdate(CirugiaBase):
    estatus: EstatusCirugia


class EstatusUpdate(BaseModel):
    estatus: EstatusCirugia
    model_config = ConfigDict(use_enum_values=True)


class CirugiaOut(BaseModel):
    id: int
    nombrePaciente: str | None = None
    edad: int
    sexo: str
    fechaCirugia: datetime
    procedimiento: str
    duracionEstimada: int
    cirujano: str
    estatus: str
    quirofano: str
    aseguradora: str | None = "No"
    serviciosEspeciales: str | None = None
    diagnostico: str | None = None
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
