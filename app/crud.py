from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models import Cirugia


def crearRegistroCirugia(
    db: Session,
    nombrePaciente: str,
    codigoPaciente: str,
    fechaCirugia: datetime,
    procedimiento: str,
    duracionEstimada: int,
    cirujano: str,
    quirofano: str,
    aseguradora: str | None,
) -> Cirugia:
    nueva_cirugia = Cirugia(
        nombrePaciente=nombrePaciente,
        codigoPaciente=codigoPaciente,
        fechaCirugia=fechaCirugia,
        procedimiento=procedimiento,
        duracionEstimada=duracionEstimada,
        cirujano=cirujano,
        estatus="PROGRAMADA",  # regla de negocio: todo alta nace programada
        quirofano=quirofano,
        aseguradora=aseguradora,
    )
    db.add(nueva_cirugia)
    db.commit()
    db.refresh(nueva_cirugia)
    return nueva_cirugia


def obtenerRegistroCirugiaPorId(db: Session, cirugia_id: int) -> Cirugia | None:
    return db.get(Cirugia, cirugia_id)


def obtenerRegistrosCirugia(db: Session) -> list[Cirugia]:
    return db.query(Cirugia).all()


def obtenerCirugiasPorRango(db: Session, desde: date, hasta: date) -> list[Cirugia]:
    """Cirugías con fecha entre `desde` y `hasta`, ambos días incluidos."""
    inicio = datetime.combine(desde, time.min)
    fin = datetime.combine(hasta, time.min) + timedelta(days=1)
    return (
        db.query(Cirugia)
        .filter(Cirugia.fechaCirugia >= inicio, Cirugia.fechaCirugia < fin)
        .order_by(Cirugia.fechaCirugia.asc())
        .all()
    )


def obtenerCirugiasPorFecha(db: Session, fecha: date) -> list[Cirugia]:
    return obtenerCirugiasPorRango(db, fecha, fecha)


def buscarTraslape(
    db: Session,
    quirofano: str,
    inicio: datetime,
    duracion: int,
    excluir_id: int | None = None,
) -> Cirugia | None:
    """Devuelve la cirugía que ocupa el quirófano en [inicio, inicio + duracion), si existe.

    Dos intervalos se traslapan si A.inicio < B.fin y A.fin > B.inicio. La duración máxima
    es 720 min, así que basta traer las que empezaron en las 24 h previas y comparar el fin
    en Python. Las FINALIZADAS no cuentan: el quirófano ya quedó libre.
    """
    fin = inicio + timedelta(minutes=duracion)
    consulta = db.query(Cirugia).filter(
        Cirugia.quirofano == quirofano,
        Cirugia.fechaCirugia < fin,
        Cirugia.fechaCirugia > inicio - timedelta(days=1),
        Cirugia.estatus != "FINALIZADA",
    )
    if excluir_id is not None:
        consulta = consulta.filter(Cirugia.id != excluir_id)
    for c in consulta.order_by(Cirugia.fechaCirugia):
        if c.fechaCirugia + timedelta(minutes=c.duracionEstimada) > inicio:
            return c
    return None


def modificarRegistroCirugia(
    db: Session,
    cirugia_id: int,
    nombrePaciente: str,
    codigoPaciente: str,
    fechaCirugia: datetime,
    procedimiento: str,
    duracionEstimada: int,
    cirujano: str,
    estatus: str,
    quirofano: str,
    aseguradora: str | None,
) -> Cirugia | None:
    cirugia = db.get(Cirugia, cirugia_id)
    if cirugia:
        cirugia.nombrePaciente = nombrePaciente
        cirugia.codigoPaciente = codigoPaciente
        cirugia.fechaCirugia = fechaCirugia
        cirugia.procedimiento = procedimiento
        cirugia.duracionEstimada = duracionEstimada
        cirugia.cirujano = cirujano
        cirugia.estatus = estatus
        cirugia.quirofano = quirofano
        cirugia.aseguradora = aseguradora
        db.commit()
        db.refresh(cirugia)
    return cirugia


def cambiarEstatusCirugia(db: Session, cirugia_id: int, estatus: str) -> Cirugia | None:
    cirugia = db.get(Cirugia, cirugia_id)
    if cirugia:
        cirugia.estatus = estatus
        db.commit()
        db.refresh(cirugia)
    return cirugia


def activarProgramadas(db: Session, ahora: datetime) -> int:
    """PROGRAMADA -> EN PROGRESO para las de HOY cuya hora de inicio ya llegó.

    Se limita al día actual para no tocar registros viejos que nadie actualizó.
    Devuelve cuántas cambió.
    """
    cambiadas = (
        db.query(Cirugia)
        .filter(
            Cirugia.estatus == "PROGRAMADA",
            Cirugia.fechaCirugia >= datetime.combine(ahora.date(), time.min),
            Cirugia.fechaCirugia <= ahora,
        )
        .update({"estatus": "EN PROGRESO"}, synchronize_session=False)
    )
    db.commit()
    return cambiadas


def finalizarVencidas(db: Session, ahora: datetime) -> int:
    """EN PROGRESO -> FINALIZADA cuando ya pasó inicio + duración estimada. Devuelve cuántas cambió."""
    en_curso = db.query(Cirugia).filter(
        Cirugia.estatus == "EN PROGRESO", Cirugia.fechaCirugia <= ahora
    )
    cambiadas = 0
    for c in en_curso:
        if c.fechaCirugia + timedelta(minutes=c.duracionEstimada) <= ahora:
            c.estatus = "FINALIZADA"
            cambiadas += 1
    db.commit()
    return cambiadas


def eliminarRegistroCirugia(db: Session, cirugia_id: int) -> Cirugia | None:
    cirugia = db.get(Cirugia, cirugia_id)
    if cirugia:
        db.delete(cirugia)
        db.commit()
    return cirugia
