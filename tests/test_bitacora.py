import io
from datetime import datetime

import pytest
from openpyxl import load_workbook

from app import crud
from app.models import Bitacora, Cirugia, Usuario


def _movimientos(client, **params):
    return client.get("/bitacora", params=params).json()["items"]


def test_alta_de_capturista_queda_registrada_con_rol_y_nombre(sesion, client, base, db):
    id_ = sesion("andrea").post("/cirugias", json=base).json()["id"]

    m = _movimientos(client)[0]
    assert m["autor"] == "capturista:Andrea_Villanueva"
    assert (m["accion"], m["entidad"], m["entidadId"]) == ("CREAR", "CIRUGIA", id_)
    assert m["detalle"]["nombrePaciente"] == "Ana López"
    assert db.get(Cirugia, id_).creadoPorId == db.query(Usuario).filter_by(usuario="andrea").one().id


def test_edicion_registra_solo_lo_que_cambio(sesion, client, base, db):
    andrea = sesion("andrea")
    id_ = andrea.post("/cirugias", json=base).json()["id"]

    andrea.put(f"/cirugias/{id_}", json={**base, "estatus": "PROGRAMADA", "edad": 46, "diagnostico": "Otro"})

    m = _movimientos(client)[0]
    assert m["accion"] == "EDITAR"
    assert m["detalle"] == {"edad": [45, 46], "diagnostico": ["Colelitiasis", "Otro"]}
    assert m["resumen"] == "Edad: 45 → 46; Diagnóstico: Colelitiasis → Otro"
    cirugia = db.get(Cirugia, id_)
    assert cirugia.actualizadoPorId is not None and cirugia.actualizadoEn is not None


def test_guardar_sin_cambios_no_registra_nada(client, crear, base):
    id_ = crear().json()["id"]
    client.put(f"/cirugias/{id_}", json={**base, "estatus": "PROGRAMADA"})

    assert [m["accion"] for m in _movimientos(client)] == ["CREAR"]


def test_cambio_de_estatus_y_eliminacion(client, crear):
    id_ = crear().json()["id"]
    client.patch(f"/cirugias/{id_}/estatus", json={"estatus": "EN PROGRESO"})
    client.delete(f"/cirugias/{id_}")

    eliminar, estatus, _ = _movimientos(client)
    assert estatus["detalle"] == {"estatus": ["PROGRAMADA", "EN PROGRESO"]}
    assert eliminar["accion"] == "ELIMINAR"
    assert eliminar["detalle"]["nombrePaciente"] == "Ana López"  # lo borrado queda en la bitácora
    assert eliminar["autor"] == "admin:Admin_Principal"


def test_scheduler_registra_como_sistema(db, crear, client):
    crear(fechaCirugia="2026-10-20T09:00")

    crud.activarProgramadas(db, datetime(2026, 10, 20, 9, 30))

    m = _movimientos(client)[0]
    assert (m["autor"], m["accion"], m["detalle"]) == ("sistema", "CAMBIAR_ESTATUS", {"estatus": ["PROGRAMADA", "EN PROGRESO"]})


def test_movimientos_de_usuarios_sin_contrasena(client, db):
    id_ = db.query(Usuario).filter_by(usuario="andrea").one().id
    client.put(f"/usuarios/{id_}/password", json={"password": "nueva-clave-1"})
    client.patch(f"/usuarios/{id_}/activo", json={"activo": False})

    desactivar, password = _movimientos(client)
    assert password["accion"] == "RESTABLECER_PASSWORD" and password["detalle"] is None
    assert desactivar["accion"] == "DESACTIVAR" and desactivar["detalle"] == {"activo": [True, False]}
    assert "nueva-clave-1" not in str(db.query(Bitacora.detalle).all())


def test_el_snapshot_conserva_rol_y_nombre_de_ese_momento(sesion, client, base, db):
    sesion("andrea").post("/cirugias", json=base)
    id_ = db.query(Usuario).filter_by(usuario="andrea").one().id
    client.put(f"/usuarios/{id_}", json={"nombre": "Andrea V. Ruiz", "rol": "ADMIN"})

    assert _movimientos(client)[-1]["autor"] == "capturista:Andrea_Villanueva"


def test_paginacion(client, crear):
    for hora in range(8, 13):
        crear(fechaCirugia=f"2026-10-20T{hora:02d}:00", duracionEstimada=60)

    r = client.get("/bitacora", params={"tamano": 2, "pagina": 3}).json()
    assert (r["total"], r["paginas"], r["pagina"], len(r["items"])) == (5, 3, 3, 1)


@pytest.mark.parametrize("quien", ["andrea", "tv"])
def test_solo_el_admin_ve_la_bitacora(sesion, quien):
    c = sesion(quien)
    assert c.get("/bitacora").status_code == 403
    assert c.get("/bitacora/exportar", params={"formato": "xlsx"}).status_code == 403


def test_exportar_bitacora_completa(sesion, client, base):
    sesion("andrea").post("/cirugias", json=base)

    r = client.get("/bitacora/exportar", params={"formato": "xlsx"})
    assert 'filename="bitacora.xlsx"' in r.headers["content-disposition"]
    hoja = load_workbook(io.BytesIO(r.content)).active
    fila = dict(zip([c.value for c in hoja[1]], [c.value for c in hoja[2]]))
    assert (fila["Usuario"], fila["Acción"]) == ("capturista:Andrea_Villanueva", "CREAR")
    assert "Paciente: Ana López" in fila["Detalle"]

    r = client.get("/bitacora/exportar", params={"formato": "pdf", "desde": "2026-01-01", "hasta": "2026-12-31"})
    assert r.content.startswith(b"%PDF")
    assert 'filename="bitacora_2026-01-01_a_2026-12-31.pdf"' in r.headers["content-disposition"]
