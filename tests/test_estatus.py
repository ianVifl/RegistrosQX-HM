"""Transiciones automáticas de estatus (las ejecuta el scheduler cada ACTUALIZAR_CADA_MIN)."""
from datetime import datetime

import pytest

from app import crud
from app.scheduler import segundos_hasta_siguiente_corte

AHORA = datetime(2026, 10, 20, 10, 0)


def nueva(db, inicio, duracion=60, estatus="PROGRAMADA"):
    c = crud.crearRegistroCirugia(
        db, nombrePaciente="Paciente", edad=30, sexo="MASCULINO", fechaCirugia=inicio,
        procedimiento="Apendicectomía", duracionEstimada=duracion, cirujano="Dr. Roberto Gómez",
        quirofano="Quirófano 1", aseguradora="No", serviciosEspeciales=None, diagnostico=None,
    )
    if estatus != "PROGRAMADA":
        crud.cambiarEstatusCirugia(db, c.id, estatus)
    return c


def test_activa_las_programadas_de_hoy_que_ya_empezaron(db):
    ya_empezo = nueva(db, datetime(2026, 10, 20, 9, 30))
    empieza_justo_ahora = nueva(db, AHORA)
    todavia_no = nueva(db, datetime(2026, 10, 20, 11, 0))
    de_ayer = nueva(db, datetime(2026, 10, 19, 9, 0))

    assert crud.activarProgramadas(db, AHORA) == 2

    db.expire_all()
    assert ya_empezo.estatus == "EN PROGRESO"
    assert empieza_justo_ahora.estatus == "EN PROGRESO"
    assert todavia_no.estatus == "PROGRAMADA"
    assert de_ayer.estatus == "PROGRAMADA"  # solo toca las de hoy


def test_finaliza_las_que_ya_terminaron(db):
    terminada = nueva(db, datetime(2026, 10, 20, 8, 0), duracion=60, estatus="EN PROGRESO")
    termina_justo_ahora = nueva(db, datetime(2026, 10, 20, 9, 0), duracion=60, estatus="EN PROGRESO")
    en_curso = nueva(db, datetime(2026, 10, 20, 9, 30), duracion=60, estatus="EN PROGRESO")

    assert crud.finalizarVencidas(db, AHORA) == 2

    db.expire_all()
    assert terminada.estatus == "FINALIZADA"
    assert termina_justo_ahora.estatus == "FINALIZADA"
    assert en_curso.estatus == "EN PROGRESO"


@pytest.mark.parametrize("ahora, cada_min, esperado", [
    (datetime(2026, 10, 20, 10, 7), 30, 23 * 60),     # siguiente corte: 10:30
    (datetime(2026, 10, 20, 10, 30), 30, 30 * 60),    # justo en un corte: el siguiente, no 0
    (datetime(2026, 10, 20, 23, 50), 30, 10 * 60),    # cruza la medianoche
    (datetime(2026, 10, 20, 10, 7, 30), 10, 150),     # con segundos
])
def test_segundos_hasta_siguiente_corte(ahora, cada_min, esperado):
    assert segundos_hasta_siguiente_corte(ahora, cada_min) == esperado
